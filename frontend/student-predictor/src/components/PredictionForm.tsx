import React, { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { UserFriendlyPredictionInput, PredictionResponse } from "@/types/api-types";
import { apiService } from "@/services/api-service";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import RiskMeter from "./RiskMeter";

// Form validation schema with natural value ranges
const predictionSchema = z.object({
  Curricular_units_2nd_sem_approved: z.coerce.number()
    .min(0, { message: "Must be at least 0" })
    .max(20, { message: "Maximum value is 20" }),
  Curricular_units_2nd_sem_grade: z.coerce.number()
    .min(0, { message: "Must be at least 0" })
    .max(20, { message: "Maximum value is 20" }),
  Tuition_fees_up_to_date: z.boolean(),
  Scholarship_holder: z.boolean(),
  Age_at_enrollment: z.coerce.number()
    .min(17, { message: "Student must be at least 17 years old" })
    .max(70, { message: "Student must be at most 70 years old" }),
  Debtor: z.boolean(),
  Gender: z.enum(["male", "female"]),
});

type PredictionFormValues = z.infer<typeof predictionSchema>;

const PredictionForm: React.FC = () => {
  const [predictionResult, setPredictionResult] = useState<PredictionResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const form = useForm<PredictionFormValues>({
    resolver: zodResolver(predictionSchema),
    defaultValues: {
      Curricular_units_2nd_sem_approved: 10,
      Curricular_units_2nd_sem_grade: 12,
      Tuition_fees_up_to_date: true,
      Scholarship_holder: false,
      Age_at_enrollment: 20,
      Debtor: false,
      Gender: "female",
    },
  });

  async function onSubmit(data: PredictionFormValues) {
    setIsSubmitting(true);
    setPredictionResult(null);
    
    try {
      // Create user-friendly input object
      const userInput: UserFriendlyPredictionInput = {
        Curricular_units_2nd_sem_approved: data.Curricular_units_2nd_sem_approved,
        Curricular_units_2nd_sem_grade: data.Curricular_units_2nd_sem_grade,
        Tuition_fees_up_to_date: data.Tuition_fees_up_to_date,
        Scholarship_holder: data.Scholarship_holder,
        Age_at_enrollment: data.Age_at_enrollment,
        Debtor: data.Debtor,
        Gender: data.Gender,
      };
      
      const result = await apiService.predict(userInput);
      
      // Validate the result to ensure the probability is a number
      const validResult: PredictionResponse = {
        probability: typeof result.probability === 'number' && !isNaN(result.probability) 
          ? result.probability 
          : 0,
        risk_level: result.risk_level || "low"
      };
      
      setPredictionResult(validResult);
      toast.success("Prediction calculated successfully");
    } catch (error) {
      console.error("Prediction error:", error);
      toast.error(error instanceof Error ? error.message : "Failed to make prediction");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Card className="md:col-span-1">
        <CardHeader>
          <CardTitle>Student Dropout Prediction</CardTitle>
          <CardDescription>
            Enter student data to predict dropout probability.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="Curricular_units_2nd_sem_approved"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Curricular Units Approved (2nd Sem)</FormLabel>
                    <FormControl>
                      <Input type="number" min="0" max="20" placeholder="0-20" {...field} />
                    </FormControl>
                    <FormDescription>
                      Number of approved curriculum units (0-20)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Curricular_units_2nd_sem_grade"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Curricular Units Grade (2nd Sem)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.1" min="0" max="20" placeholder="0-20" {...field} />
                    </FormControl>
                    <FormDescription>
                      Average grade (0-20 scale)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Tuition_fees_up_to_date"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>Tuition Fees Up-to-Date</FormLabel>
                      <FormDescription>
                        Is the student's tuition payment up to date?
                      </FormDescription>
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Scholarship_holder"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>Scholarship Holder</FormLabel>
                      <FormDescription>
                        Does the student have a scholarship?
                      </FormDescription>
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Age_at_enrollment"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Age at Enrollment</FormLabel>
                    <FormControl>
                      <Input type="number" min="17" max="70" placeholder="17-70" {...field} />
                    </FormControl>
                    <FormDescription>
                      Student's age when they enrolled (17-70)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Debtor"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>Debtor</FormLabel>
                      <FormDescription>
                        Is the student a debtor?
                      </FormDescription>
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Gender"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gender</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        className="flex space-x-4"
                      >
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="male" />
                          </FormControl>
                          <FormLabel className="font-normal">Male</FormLabel>
                        </FormItem>
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="female" />
                          </FormControl>
                          <FormLabel className="font-normal">Female</FormLabel>
                        </FormItem>
                      </RadioGroup>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Calculating..." : "Predict Dropout Risk"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
      
      <Card className="md:col-span-1">
        <CardHeader>
          <CardTitle>Prediction Result</CardTitle>
          <CardDescription>
            Risk level assessment based on student data
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center">
          {predictionResult ? (
            <>
              <RiskMeter 
                probability={predictionResult.probability} 
                riskLevel={predictionResult.risk_level} 
              />
              <div className="text-center mt-6">
                <p className="text-xl font-medium mb-1">
                  Dropout Risk: 
                  <span 
                    className={`ml-2 font-bold ${
                      predictionResult.risk_level === "high" 
                        ? "text-red-600" 
                        : predictionResult.risk_level === "medium" 
                        ? "text-orange-500" 
                        : "text-green-600"
                    }`}
                  >
                    {predictionResult.risk_level.toUpperCase()}
                  </span>
                </p>
                <p className="text-sm text-muted-foreground">
                  Probability: {(typeof predictionResult.probability === 'number' && !isNaN(predictionResult.probability) 
                    ? (predictionResult.probability * 100).toFixed(1) 
                    : "0")}%
                </p>
              </div>
            </>
          ) : (
            <div className="text-center py-12 px-4">
              <p className="text-muted-foreground">
                Fill out the form and submit to see the dropout risk prediction.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PredictionForm;