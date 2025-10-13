"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Loader2, FileSearch, Brain, Shield, Check } from "lucide-react";

interface LoadingAnimationProps {
  fileName: string;
  fileType: string;
}

type ProcessingStage = {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  duration: number;
};

const stages: ProcessingStage[] = [
  {
    id: "reading",
    label: "Leyendo archivo",
    description: "Extrayendo contenido del documento...",
    icon: <FileSearch className="w-5 h-5" />,
    duration: 2000,
  },
  {
    id: "analyzing",
    label: "Analizando con patrones",
    description: "Detectando datos sensibles con expresiones regulares...",
    icon: <Shield className="w-5 h-5" />,
    duration: 2000,
  },
  {
    id: "ai",
    label: "Análisis con IA",
    description: "Usando Gemini AI para detección inteligente...",
    icon: <Brain className="w-5 h-5" />,
    duration: 3000,
  },
  {
    id: "processing",
    label: "Procesando resultados",
    description: "Generando documento con subrayado...",
    icon: <Loader2 className="w-5 h-5 animate-spin" />,
    duration: 2000,
  },
];

export function LoadingAnimation({ fileName, fileType }: LoadingAnimationProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [stageProgress, setStageProgress] = useState(0);

  useEffect(() => {
    // Calcular progreso total
    const totalDuration = stages.reduce((sum, stage) => sum + stage.duration, 0);
    let elapsed = 0;

    const interval = setInterval(() => {
      elapsed += 50;

      // Calcular en qué etapa estamos
      let cumulativeDuration = 0;
      let newStage = 0;

      for (let i = 0; i < stages.length; i++) {
        cumulativeDuration += stages[i].duration;
        if (elapsed < cumulativeDuration) {
          newStage = i;
          break;
        }
      }

      // Calcular progreso de la etapa actual
      const stageStart = stages.slice(0, newStage).reduce((sum, s) => sum + s.duration, 0);
      const stageDuration = stages[newStage]?.duration || 1;
      const stageElapsed = elapsed - stageStart;
      const newStageProgress = Math.min((stageElapsed / stageDuration) * 100, 100);

      setCurrentStage(newStage);
      setStageProgress(newStageProgress);
      setProgress(Math.min((elapsed / totalDuration) * 100, 95));

      if (elapsed >= totalDuration) {
        clearInterval(interval);
      }
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const isPdf = fileType === "application/pdf";

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <Card className="border-2 border-primary/20 shadow-lg">
        <CardHeader className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping" />
              <div className="relative bg-primary/10 p-4 rounded-full">
                <Brain className="w-12 h-12 text-primary animate-pulse" />
              </div>
            </div>
          </div>
          <CardTitle className="text-2xl">Analizando documento</CardTitle>
          <CardDescription className="text-base">
            <span className="font-medium">{fileName}</span>
            {isPdf ? " (PDF)" : " (Texto)"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Barra de progreso general */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Progreso general</span>
              <span className="font-medium">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Etapas del proceso */}
          <div className="space-y-3">
            {stages.map((stage, index) => {
              const isCompleted = index < currentStage;
              const isCurrent = index === currentStage;
              const isPending = index > currentStage;

              return (
                <div
                  key={stage.id}
                  className={`flex items-start gap-3 p-3 rounded-lg transition-all duration-300 ${
                    isCurrent
                      ? "bg-primary/10 border-2 border-primary/30 scale-105"
                      : isCompleted
                      ? "bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900"
                      : "bg-secondary/30 border border-transparent opacity-60"
                  }`}
                >
                  {/* Icono */}
                  <div
                    className={`mt-0.5 ${
                      isCurrent
                        ? "text-primary"
                        : isCompleted
                        ? "text-green-600 dark:text-green-400"
                        : "text-muted-foreground"
                    }`}
                  >
                    {isCompleted ? (
                      <Check className="w-5 h-5" />
                    ) : (
                      stage.icon
                    )}
                  </div>

                  {/* Contenido */}
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <h4
                        className={`font-medium ${
                          isCurrent
                            ? "text-primary"
                            : isCompleted
                            ? "text-green-600 dark:text-green-400"
                            : "text-muted-foreground"
                        }`}
                      >
                        {stage.label}
                      </h4>
                      {isCurrent && (
                        <span className="text-xs font-medium text-primary">
                          {Math.round(stageProgress)}%
                        </span>
                      )}
                      {isCompleted && (
                        <span className="text-xs font-medium text-green-600 dark:text-green-400">
                          Completado
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {stage.description}
                    </p>
                    {isCurrent && (
                      <Progress value={stageProgress} className="h-1 mt-2" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Mensaje final */}
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg">
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
              <div className="space-y-1">
                <h5 className="font-medium text-blue-900 dark:text-blue-100">
                  Procesamiento seguro
                </h5>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  Tu documento se procesa localmente. Los datos sensibles serán
                  subrayados en rojo para fácil identificación.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Animación decorativa */}
      <div className="flex justify-center gap-2">
        <div className="w-3 h-3 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
        <div className="w-3 h-3 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
        <div className="w-3 h-3 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  );
}
