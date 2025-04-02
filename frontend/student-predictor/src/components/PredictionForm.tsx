import React, { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { PredictionInput, PredictionResponse } from "@/types/api-types";
import { apiService } from "@/services/api-service";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { toast } from "sonner";
import RiskMeter from "./RiskMeter";

// Form validation schema
const predictionSchema = z.object({
  Curricular_units_2nd_sem_approved: z.coerce.number()
    .min(-2.9, { message: "Minimum value is -2.9" })
    .max(2.5, { message: "Maximum value is 2.5" }),
  Curricular_units_2nd_sem_grade: z.coerce.number(),
  Tuition_fees_up_to_date: z.enum(["0", "1"]).transform(val => parseInt(val)),
  Scholarship_holder: z.enum(["0", "1"]).transform(val => parseInt(val)),
  Age_at_enrollment: z.coerce.number(),
  Debtor: z.enum(["0", "1"]).transform(val => parseInt(val)),
  Gender: z.enum(["male", "female"]),
});

type PredictionFormValues = z.infer<typeof predictionSchema>;

const PredictionForm: React.FC = () => {
  const [predictionResult, setPredictionResult] = useState<PredictionResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const form = useForm<PredictionFormValues>({
    resolver: zodResolver(predictionSchema),
    defaultValues: {
      Curricular_units_2nd_sem_approved: 0,
      Curricular_units_2nd_sem_grade: 0,
      Tuition_fees_up_to_date: "1",
      Scholarship_holder: "0",
      Age_at_enrollment: 0,
      Debtor: "0",
      Gender: "female",
    },
  });

  async function onSubmit(data: PredictionFormValues) {
    setIsSubmitting(true);
    setPredictionResult(null);
    
    try {
      // Transform the data to match the expected PredictionInput type
      const predictionInput: PredictionInput = {
        Curricular_units_2nd_sem_approved: data.Curricular_units_2nd_sem_approved,
        Curricular_units_2nd_sem_grade: data.Curricular_units_2nd_sem_grade,
        Tuition_fees_up_to_date: data.Tuition_fees_up_to_date,
        Scholarship_holder: data.Scholarship_holder,
        Age_at_enrollment: data.Age_at_enrollment,
        Debtor: data.Debtor,
        Gender: data.Gender,
      };
      
      const result = await apiService.predict(predictionInput);
      setPredictionResult(result);
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
                      <Input type="number" step="0.1" placeholder="-2.9 to 2.5" {...field} />
                    </FormControl>
                    <FormDescription>
                      Standardized value between -2.9 and 2.5
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
                      <Input type="number" step="0.1" placeholder="Standardized value" {...field} />
                    </FormControl>
                    <FormDescription>
                      Standardized value
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Tuition_fees_up_to_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tuition Fees Up-to-Date?</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        className="flex space-x-4"
                      >
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="1" />
                          </FormControl>
                          <FormLabel className="font-normal">Yes</FormLabel>
                        </FormItem>
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="0" />
                          </FormControl>
                          <FormLabel className="font-normal">No</FormLabel>
                        </FormItem>
                      </RadioGroup>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Scholarship_holder"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Scholarship Holder?</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        className="flex space-x-4"
                      >
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="1" />
                          </FormControl>
                          <FormLabel className="font-normal">Yes</FormLabel>
                        </FormItem>
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="0" />
                          </FormControl>
                          <FormLabel className="font-normal">No</FormLabel>
                        </FormItem>
                      </RadioGroup>
                    </FormControl>
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
                      <Input type="number" step="0.1" placeholder="Standardized value" {...field} />
                    </FormControl>
                    <FormDescription>
                      Standardized value
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="Debtor"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Is Debtor?</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        className="flex space-x-4"
                      >
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="1" />
                          </FormControl>
                          <FormLabel className="font-normal">Yes</FormLabel>
                        </FormItem>
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="0" />
                          </FormControl>
                          <FormLabel className="font-normal">No</FormLabel>
                        </FormItem>
                      </RadioGroup>
                    </FormControl>
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
              <RiskMeter probability={predictionResult.probability} riskLevel={predictionResult.risk_level} />
              <div className="text-center mt-6">
                <p className="text-xl font-medium mb-1">
                  Dropout Risk: 
                  <span 
                    className={`ml-2 font-bold ${
                      predictionResult.risk_level === "high" 
                        ? "text-risk-high" 
                        : predictionResult.risk_level === "medium" 
                        ? "text-risk-medium" 
                        : "text-green-600"
                    }`}
                  >
                    {predictionResult.risk_level.toUpperCase()}
                  </span>
                </p>
                <p className="text-sm text-muted-foreground">
                  Probability: {(predictionResult.probability * 100).toFixed(1)}%
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