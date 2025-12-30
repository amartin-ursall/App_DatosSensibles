"use client";

import { useEffect, useMemo, useState } from "react";
import type { ProcessingProgress } from "@/lib/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Loader2,
  FileSearch,
  Brain,
  Shield,
  Check,
  Scan,
  Cpu,
  Highlighter,
  FileCog,
} from "lucide-react";

interface LoadingAnimationProps {
  fileName: string;
  fileType: string;
  extractionMode?: "parser" | "ocr" | null;
  fileSize?: number;
  progressData?: ProcessingProgress | null;
}

type ProcessingStage = {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  duration: number;
};

const buildStages = (
  mode: "parser" | "ocr" | null | undefined,
  fileSize?: number
): ProcessingStage[] => {
  const fileSizeMb = fileSize ? fileSize / (1024 * 1024) : 0;

  if (mode === "ocr") {
    const initFactor = fileSizeMb ? Math.min(2, 1 + fileSizeMb / 12) : 1;
    const ocrFactor = fileSizeMb ? Math.min(3, 1 + fileSizeMb / 6) : 1.2;
    const redactFactor = fileSizeMb ? Math.min(2.2, 1 + fileSizeMb / 10) : 1.1;

    return [
      {
        id: "prepare",
        label: "Preparando motor OCR",
        description: "Verificando dependencias y espacio temporal para el OCR...",
        icon: <Scan className="w-5 h-5" />,
        duration: Math.round(1800 * initFactor),
      },
      {
        id: "model",
        label: "Cargando modelo TrOCR",
        description: "Inicializando pesos del modelo de reconocimiento de texto...",
        icon: <Cpu className="w-5 h-5" />,
        duration: Math.round(2600 * initFactor),
      },
      {
        id: "ocr",
        label: "Analizando páginas con OCR",
        description: "Reconociendo texto en cada página del documento escaneado...",
        icon: <Brain className="w-5 h-5" />,
        duration: Math.round(4500 * ocrFactor),
      },
      {
        id: "redact",
        label: "Aplicando redacciones negras",
        description: "Enmascarando datos sensibles con bloques negros sólidos...",
        icon: <Highlighter className="w-5 h-5" />,
        duration: Math.round(3200 * redactFactor),
      },
      {
        id: "final",
        label: "Generando PDF final",
        description: "Optimizando y guardando el documento protegido...",
        icon: <Loader2 className="w-5 h-5 animate-spin" />,
        duration: 2200,
      },
    ];
  }

  const parserFactor = fileSizeMb ? Math.min(2, 1 + fileSizeMb / 10) : 1;

  return [
    {
      id: "reading",
      label: "Leyendo documento",
      description: "Extrayendo texto y metadatos del archivo...",
      icon: <FileSearch className="w-5 h-5" />,
      duration: Math.round(1800 * parserFactor),
    },
    {
      id: "parser",
      label: "Parser estructurado",
      description: "Analizando el contenido nativo página por página...",
      icon: <FileCog className="w-5 h-5" />,
      duration: Math.round(2400 * parserFactor),
    },
    {
      id: "detection",
      label: "Detectando datos sensibles",
      description: "Aplicando reglas y validaciones de confidencialidad...",
      icon: <Shield className="w-5 h-5" />,
      duration: 2600,
    },
    {
      id: "render",
      label: "Generando documento protegido",
      description: "Aplicando redacciones y preparando la descarga...",
      icon: <Loader2 className="w-5 h-5 animate-spin" />,
      duration: 2200,
    },
  ];
};

const STAGE_DETAILS: Record<string, { label: string; description: string }> = {
  preparing: {
    label: "Preparando documento",
    description: "Inicializando el procesamiento y validando la configuración.",
  },
  queued: {
    label: "Archivo recibido",
    description: "El documento se ha cargado correctamente y está en cola.",
  },
  "saved-input": {
    label: "Entrada almacenada",
    description: "Guardando el archivo para su procesamiento seguro.",
  },
  "image-converted": {
    label: "Imagen convertida a PDF",
    description: "Se generó un PDF temporal a partir del archivo escaneado.",
  },
  "starting-processing": {
    label: "Iniciando procesamiento",
    description: "Preparando el pipeline de detección y redacción.",
  },
  "parsing-external": {
    label: "Parser estructurado",
    description: "Analizando el contenido textual del PDF original.",
  },
  "ocr-initializing": {
    label: "Inicializando OCR",
    description: "Cargando el modelo TrOCR para reconocer texto en imágenes.",
  },
  "opening-document": {
    label: "Abriendo documento",
    description: "Cargando las páginas del PDF para analizarlas una a una.",
  },
  "parser-page": {
    label: "Procesando página estructurada",
    description: "Detectando datos sensibles en el contenido con texto nativo.",
  },
  "ocr-page": {
    label: "Reconociendo texto (OCR)",
    description: "Extrayendo texto de la página escaneada mediante OCR.",
  },
  finalizing: {
    label: "Generando PDF protegido",
    description: "Aplicando redacciones y optimizando el documento final.",
  },
  completed: {
    label: "Proceso completado",
    description: "El documento se redactó correctamente.",
  },
  error: {
    label: "Error durante el procesamiento",
    description: "Se produjo un problema. Revisa el mensaje para más detalles.",
  },
};

const OCR_STAGE_FLOW = [
  "queued",
  "saved-input",
  "image-converted",
  "starting-processing",
  "ocr-initializing",
  "opening-document",
  "ocr-page",
  "finalizing",
  "completed",
];

const PARSER_STAGE_FLOW = [
  "queued",
  "saved-input",
  "starting-processing",
  "parsing-external",
  "opening-document",
  "parser-page",
  "finalizing",
  "completed",
];

export function LoadingAnimation({
  fileName,
  fileType,
  extractionMode,
  fileSize,
  progressData,
}: LoadingAnimationProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [stageProgress, setStageProgress] = useState(0);

  const stages = useMemo(
    () => buildStages(extractionMode, fileSize),
    [extractionMode, fileSize]
  );

  const hasDynamicProgress = Boolean(progressData);
  const displayPercent = hasDynamicProgress
    ? Math.min(100, Math.max(0, progressData?.percent ?? 0))
    : progress;
  const stageKey = hasDynamicProgress
    ? progressData?.stage ?? (extractionMode === "ocr" ? "ocr-page" : "parser-page")
    : stages[currentStage]?.id ?? (extractionMode === "ocr" ? "ocr" : "processing");
  const stageInfo =
    STAGE_DETAILS[stageKey] ?? {
      label: stageKey,
      description: "Procesando documento...",
    };
  const currentPageValue =
    progressData && typeof progressData.currentPage === "number"
      ? progressData.currentPage
      : null;
  const totalPagesValue =
    progressData && typeof progressData.totalPages === "number"
      ? progressData.totalPages
      : null;
  const currentPageLabel =
    currentPageValue && currentPageValue > 0
      ? totalPagesValue && totalPagesValue > 0
        ? `Pagina ${Math.min(currentPageValue, totalPagesValue)} de ${totalPagesValue}`
        : `Pagina ${currentPageValue}`
      : null;
  const extractionLabel = progressData?.extractionMethod
    ? progressData.extractionMethod.toUpperCase()
    : extractionMode ?? undefined;

  useEffect(() => {
    if (progressData) {
      const pct = Math.min(100, Math.max(0, progressData.percent ?? 0));
      setProgress(pct);
      setStageProgress(pct);
      return;
    }

    if (stages.length === 0) {
      setProgress(100);
      setStageProgress(100);
      return;
    }

    setCurrentStage(0);
    setStageProgress(0);
    setProgress(0);

    const cumulativeDurations = stages.reduce<number[]>((acc, stage) => {
      const previous = acc.length > 0 ? acc[acc.length - 1] : 0;
      acc.push(previous + stage.duration);
      return acc;
    }, []);

    const totalDuration = cumulativeDurations[cumulativeDurations.length - 1];
    let elapsed = 0;

    const interval = window.setInterval(() => {
      elapsed += 80;

      if (elapsed >= totalDuration) {
        setCurrentStage(stages.length - 1);
        setStageProgress(100);
        setProgress(100);
        window.clearInterval(interval);
        return;
      }

      let stageIndex = stages.length - 1;
      for (let i = 0; i < cumulativeDurations.length; i++) {
        if (elapsed < cumulativeDurations[i]) {
          stageIndex = i;
          break;
        }
      }

      const stageStart = stageIndex === 0 ? 0 : cumulativeDurations[stageIndex - 1];
      const stageDuration = stages[stageIndex].duration || 1;
      const stageElapsed = elapsed - stageStart;
      const stageProgressValue = Math.min(
        100,
        (stageElapsed / stageDuration) * 100
      );

      setCurrentStage(stageIndex);
      setStageProgress(stageProgressValue);
      setProgress(Math.min(99, (elapsed / totalDuration) * 100));
    }, 80);

    return () => window.clearInterval(interval);
  }, [progressData, stages]);

  const isPdf = fileType === "application/pdf";
  const headerTitle =
    extractionMode === "ocr" ? "Ejecutando OCR avanzado" : "Analizando documento";
  const headerIcon =
    extractionMode === "ocr" ? (
      <Scan className="w-12 h-12 text-primary animate-pulse" />
    ) : (
      <Brain className="w-12 h-12 text-primary animate-pulse" />
    );

  const infoMessage =
    extractionMode === "ocr"
      ? "Tu documento escaneado se procesa localmente. Los datos sensibles se ocultan con bloques negros antes de generar el PDF final."
      : "Tu documento se procesa localmente. Los datos sensibles se ocultan antes de devolver el resultado.";

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <Card className="border-2 border-primary/20 shadow-lg">
        <CardHeader className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping" />
              <div className="relative bg-primary/10 p-4 rounded-full">
                {headerIcon}
              </div>
            </div>
          </div>
          <CardTitle className="text-2xl">{headerTitle}</CardTitle>
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
              <span className="font-medium">{Math.round(displayPercent)}%</span>
            </div>
            <Progress value={displayPercent} className="h-2" />
          </div>

          {/* Etapas del proceso */}
          <div className="space-y-3">
            {hasDynamicProgress ? (
              <>
                <div className="p-4 rounded-lg border border-primary/30 bg-primary/10">
                  <p className="text-xs font-medium uppercase text-primary tracking-wide">
                    Estado
                  </p>
                  <p className="text-lg font-semibold text-primary mt-1">{stageInfo.label}</p>
                  <p className="text-sm text-muted-foreground">{stageInfo.description}</p>
                  {currentPageLabel && (
                    <p className="text-sm text-muted-foreground mt-2">
                      <span className="font-medium text-primary">Pagina:</span> {currentPageLabel}
                    </p>
                  )}
                  {extractionLabel && (
                    <p className="text-sm text-muted-foreground">
                      <span className="font-medium text-primary">Modo:</span>{" "}
                      {extractionLabel.toUpperCase()}
                    </p>
                  )}
                </div>
                {progressData?.message && (
                  <div className="p-3 rounded-lg border border-destructive/40 bg-destructive/10 text-sm text-destructive">
                    {progressData.message}
                  </div>
                )}
              </>
            ) : (
              stages.map((stage, index) => {
                const isCompleted = index < currentStage;
                const isCurrent = index === currentStage;

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
                      {isCompleted ? <Check className="w-5 h-5" /> : stage.icon}
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
              })
            )}
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
                  {infoMessage}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Animación decorativa */}
      <div className="flex justify-center gap-2">
        <div
          className="w-3 h-3 bg-primary rounded-full animate-bounce"
          style={{ animationDelay: "0ms" }}
        />
        <div
          className="w-3 h-3 bg-primary rounded-full animate-bounce"
          style={{ animationDelay: "150ms" }}
        />
        <div
          className="w-3 h-3 bg-primary rounded-full animate-bounce"
          style={{ animationDelay: "300ms" }}
        />
      </div>
    </div>
  );
}
