"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  SidebarProvider,
  Sidebar,
  SidebarInset,
  SidebarHeader,
  SidebarContent,
} from "@/components/ui/sidebar";
import {
  RedactionRules,
  RedactionStrategy,
  SensitivityLevel,
  supportedFileTypes,
  ProcessingProgress,
} from "@/lib/types";
import { ALL_RULES, RedactionSettings } from "@/components/app/redaction-settings";
import { FileUploader } from "@/components/app/file-uploader";
import { useToast } from "@/hooks/use-toast";
// Eliminado: procesamiento y detección en TS
import { ResultsView } from "@/components/app/results-view";
import { Button } from "@/components/ui/button";

export default function PrivacyPalPage() {
  const [file, setFile] = useState<File | null>(null);
  const [originalContent, setOriginalContent] = useState<string | null>(null);
  const [redactedContent, setRedactedContent] = useState<string | Blob | null>(
    null
  );
  const [detectionStats, setDetectionStats] = useState<{
    total: number;
    byType: Record<string, number>;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [extractionMode, setExtractionMode] = useState<"parser" | "ocr" | null>(
    null
  );
  const [processingProgress, setProcessingProgress] = useState<ProcessingProgress | null>(null);
  const progressPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const { toast } = useToast();

  const rawApiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000";
  const apiBaseUrl = rawApiUrl.replace(/\/$/, "");
  const processPdfUrl = `${apiBaseUrl}/api/process-pdf`;
  const detectTextUrl = `${apiBaseUrl}/api/detect-text`;

  const stopProgressPolling = useCallback(() => {
    if (progressPollRef.current) {
      clearInterval(progressPollRef.current);
      progressPollRef.current = null;
    }
  }, []);

  const startProgressPolling = useCallback(
    (progressId: string) => {
      stopProgressPolling();
      const endpoint = `${apiBaseUrl}/api/progress/${progressId}`;

      progressPollRef.current = setInterval(async () => {
        try {
          const response = await fetch(endpoint, { cache: "no-store" });
          if (!response.ok) {
            if (response.status === 404) {
              return;
            }
            throw new Error(`Progress request failed with status ${response.status}`);
          }

          const data = await response.json();
          setProcessingProgress({
            stage: typeof data.stage === "string" ? data.stage : "processing",
            percent: typeof data.percent === "number" ? data.percent : 0,
            currentPage: typeof data.currentPage === "number" ? data.currentPage : undefined,
            totalPages: typeof data.totalPages === "number" ? data.totalPages : undefined,
            extractionMethod: typeof data.extractionMethod === "string" ? data.extractionMethod : undefined,
            message: typeof data.message === "string" ? data.message : undefined,
            done: Boolean(data.done),
            updatedAt: typeof data.updatedAt === "number" ? data.updatedAt : Date.now(),
          });

          if (data.done) {
            stopProgressPolling();
          }
        } catch (pollError) {
          console.error("[progress] Error polling backend:", pollError);
        }
      }, 1000);
    },
    [apiBaseUrl, stopProgressPolling]
  );

  useEffect(() => {
    return () => {
      stopProgressPolling();
    };
  }, [stopProgressPolling]);

  const [rules, setRules] = useState<RedactionRules>(() =>
    ALL_RULES.reduce(
      (acc, rule) => ({ ...acc, [rule.id]: true }),
      {} as RedactionRules
    )
  );
  const sensitivityLevel: SensitivityLevel = "strict"; // Siempre en modo estricto
  const strategy: RedactionStrategy = "underline"; // Solo modo subrayado

  const underlineMatches = (text: string, matches: Array<{ start: number; end: number }>): string => {
    if (!matches || matches.length === 0) return text;
    // Ordenar por inicio para aplicar en secuencia
    const sorted = [...matches].sort((a, b) => a.start - b.start);
    let result = "";
    let cursor = 0;
    for (const m of sorted) {
      const start = Math.max(0, Math.min(m.start, text.length));
      const end = Math.max(start, Math.min(m.end, text.length));
      if (start > cursor) {
        result += text.slice(cursor, start);
      }
      result += `__${text.slice(start, end)}__`;
      cursor = end;
    }
    if (cursor < text.length) {
      result += text.slice(cursor);
    }
    return result;
  };

  const handleRuleChange = (ruleId: keyof RedactionRules, enabled: boolean) => {
    setRules((prev) => ({ ...prev, [ruleId]: enabled }));
  };

  const handleFileProcess = useCallback(
    async (uploadedFile: File) => {
      if (isLoading) return;

      stopProgressPolling();
      setProcessingProgress(null);

      const fileType =
        uploadedFile.type || `text/x-${uploadedFile.name.split(".").pop()}`;

      if (
        !supportedFileTypes.includes(fileType) &&
        !uploadedFile.name.endsWith(".log")
      ) {
        toast({
          variant: "destructive",
          title: "Tipo de Archivo no Soportado",
          description: `Lo sentimos, no soportamos archivos de tipo "${
            uploadedFile.name.split(".").pop() || "desconocido"
          }".`,
        });
        return;
      }

      if (
        uploadedFile.type === "application/pdf" &&
        extractionMode === null
      ) {
        toast({
          variant: "destructive",
          title: "Selecciona el tipo de documento",
          description:
            "Indica si el PDF es digital o escaneado antes de continuar.",
        });
        return;
      }

      setIsLoading(true);
      setFile(uploadedFile);
      setOriginalContent(null);
      setRedactedContent(null);
      setDetectionStats(null);

      let progressId: string | null = null;

      try {
        if (uploadedFile.type === "application/pdf") {
          // Procesar PDF en el backend Python
          console.log("[PDF] Enviando PDF al backend...");
          console.log("[PDF] Archivo:", uploadedFile.name, "- Tamano:", uploadedFile.size, "bytes");
          console.log(
            "[PDF] Reglas activas:",
            Object.entries(rules)
              .filter(([_, v]) => v)
              .map(([k]) => k)
          );
          console.log("[PDF] Nivel de sensibilidad:", sensitivityLevel);
          const forcedExtractionMode = extractionMode ?? "parser";
          const pdfAction = forcedExtractionMode === "ocr" ? "redact" : "highlight";
          console.log("[PDF] Modo de extraccion:", forcedExtractionMode);
          console.log("[PDF] Tipo de marcaje:", pdfAction);
          console.log("[PDF] Endpoint:", processPdfUrl);

          const newProgressId =
            typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
              ? crypto.randomUUID()
              : `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
          progressId = newProgressId;
          setProcessingProgress({
            stage: "queued",
            percent: 1,
            currentPage: 0,
            totalPages: undefined,
            extractionMethod: forcedExtractionMode,
            done: false,
            updatedAt: Date.now(),
          });
          startProgressPolling(newProgressId);

          const formData = new FormData();
          formData.append("file", uploadedFile);
          formData.append("rules", JSON.stringify(rules));
          formData.append("sensitivityLevel", sensitivityLevel);
          formData.append("action", pdfAction);
          formData.append("extractionMode", forcedExtractionMode);
          formData.append("progressId", newProgressId);

          const startTime = performance.now();

          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 30 * 60 * 1000);

          try {
            const response = await fetch(processPdfUrl, {
              method: "POST",
              body: formData,
              signal: controller.signal,
            });

            clearTimeout(timeoutId);

            const endTime = performance.now();
            const duration = ((endTime - startTime) / 1000).toFixed(2);

            console.log("[PDF] Respuesta recibida");
            console.log("[PDF] Tiempo de respuesta:", duration, "segundos");
            console.log("[PDF] Status:", response.status, response.statusText);

            if (!response.ok) {
              console.error("[PDF] Error en la respuesta:", response.status, response.statusText);
              throw new Error("Error al procesar PDF en el backend Python");
            }

            const pdfBlob = await response.blob();
            const totalMatches = parseInt(response.headers.get("X-Total-Matches") || "0");
            const matchesByType = JSON.parse(response.headers.get("X-Matches-By-Type") || "{}");
            const processedPagesHeader = response.headers.get("X-Pages-Processed");
            const parsedProcessedPages = processedPagesHeader ? Number.parseInt(processedPagesHeader, 10) : NaN;
            const processedPages = Number.isNaN(parsedProcessedPages) ? undefined : parsedProcessedPages;

            if (progressId) {
              setProcessingProgress((prev) => ({
                stage: "completed",
                percent: 100,
                currentPage: processedPages ?? prev?.currentPage ?? prev?.totalPages ?? undefined,
                totalPages: processedPages ?? prev?.totalPages,
                extractionMethod: prev?.extractionMethod ?? forcedExtractionMode,
                done: true,
                message: undefined,
                updatedAt: Date.now(),
              }));
            }

            console.log("[PDF] PDF procesado correctamente");
            console.log("[PDF] Total de coincidencias:", totalMatches);
            console.log("[PDF] Coincidencias por tipo:", matchesByType);
            console.log("[PDF] Tamano del PDF procesado:", pdfBlob.size, "bytes");

            setRedactedContent(pdfBlob);
            setDetectionStats({
              total: totalMatches,
              byType: matchesByType,
            });

            toast({
              title: "PDF procesado con backend Python",
              description: `Se detectaron ${totalMatches} dato(s) sensible(s).`,
            });
          } catch (fetchError) {
            clearTimeout(timeoutId);
            if (fetchError instanceof Error && fetchError.name === "AbortError") {
              console.error("[PDF] Timeout de 30 minutos alcanzado");
              throw new Error("El procesamiento del PDF tardo mas de 30 minutos");
            }
            throw fetchError;
          }
        } else {
          console.log("[TEXTO] Enviando texto al backend...");
          console.log("[TEXTO] Archivo:", uploadedFile.name, "- Tipo:", uploadedFile.type);

          const text = await uploadedFile.text();
          console.log("[TEXTO] Longitud del texto:", text.length, "caracteres");
          console.log(
            "[TEXTO] Reglas activas:",
            Object.entries(rules)
              .filter(([_, v]) => v)
              .map(([k]) => k)
          );
          console.log("[TEXTO] Nivel de sensibilidad:", sensitivityLevel);
          console.log("[TEXTO] Endpoint:", detectTextUrl);

          setOriginalContent(text);

          const startTime = performance.now();

          const response = await fetch(detectTextUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text,
              rules,
              sensitivityLevel,
            }),
          });

          const endTime = performance.now();
          const duration = ((endTime - startTime) / 1000).toFixed(2);

          console.log("[TEXTO] Respuesta recibida");
          console.log("[TEXTO] Tiempo de respuesta:", duration, "segundos");
          console.log("[TEXTO] Status:", response.status, response.statusText);

          if (!response.ok) {
            console.error("[TEXTO] Error en la respuesta:", response.status, response.statusText);
            throw new Error("Error al detectar texto en el backend Python");
          }

          const data = await response.json();
          console.log("[TEXTO] Texto procesado correctamente");
          console.log("[TEXTO] Total de coincidencias:", data.stats?.total || 0);
          console.log("[TEXTO] Coincidencias por tipo:", data.stats?.by_type || {});
          console.log("[TEXTO] Numero de matches:", data.matches?.length || 0);

          const underlined = underlineMatches(text, data.matches || []);
          setRedactedContent(underlined);
          setDetectionStats({
            total: data.stats?.total || 0,
            byType: data.stats?.by_type || {},
          });

          toast({
            title: "Texto analizado en backend Python",
            description: `Se detectaron ${data.stats.total} dato(s) sensible(s).`,
          });

        }
      } catch (error) {
        console.error("❌ Error processing file:", error);
        console.error("❌ Detalles del error:", {
          message: error instanceof Error ? error.message : "Error desconocido",
          stack: error instanceof Error ? error.stack : undefined,
        });
        toast({
          variant: "destructive",
          title: "Error de Procesamiento",
          description: "Hubo un error al procesar tu archivo. El PDF podría estar malformado o encriptado.",
        });
        handleReset();
      } finally {
        console.log('[FINALIZADO] Procesamiento finalizado');
        stopProgressPolling();
          setIsLoading(false);
      }
    },
    [
      extractionMode,
      isLoading,
      rules,
      strategy,
      sensitivityLevel,
      startProgressPolling,
      stopProgressPolling,
      toast,
    ]
  );

  const handleReset = () => {
    stopProgressPolling();
    setProcessingProgress(null);
    setFile(null);
    setOriginalContent(null);
    setRedactedContent(null);
    setDetectionStats(null);
    setIsLoading(false);
    setExtractionMode(null);
  };

  return (
    <SidebarProvider>
      <div className="flex min-h-svh w-full">
        <Sidebar collapsible="none" className="p-0">
          <SidebarContent className="p-4">
            <RedactionSettings
              rules={rules}
              onRuleChange={handleRuleChange}
              isPdf={file?.type === "application/pdf"}
            />
          </SidebarContent>
        </Sidebar>
        <SidebarInset className="bg-background">
          <main className="flex flex-1 flex-col items-center p-4 sm:p-6 pb-8">
            <div className="w-full max-w-7xl mx-auto">
              {!file ? (
                <>
                  <section className="mb-6">
                    <h2 className="text-lg font-semibold">
                      Selecciona el tipo de documento
                    </h2>
                    <p className="text-sm text-muted-foreground mb-4">
                      Indica si el PDF es digital o si es una imagen escaneada
                      para que el proceso use parser o OCR segun corresponda.
                    </p>
                    <div className="grid gap-3 sm:grid-cols-2">
                      <Button
                        type="button"
                        variant={extractionMode === "parser" ? "default" : "outline"}
                        className="flex h-auto flex-col items-start gap-2 py-4 text-left"
                        onClick={() => setExtractionMode("parser")}
                        disabled={isLoading}
                      >
                        <span className="text-base font-medium">
                          Documento digital
                        </span>
                        <span className="text-sm text-muted-foreground">
                          Usa parser estructurado para PDFs con texto
                          seleccionable o generados desde origen electronico.
                        </span>
                      </Button>
                      <Button
                        type="button"
                        variant={extractionMode === "ocr" ? "default" : "outline"}
                        className="flex h-auto flex-col items-start gap-2 py-4 text-left"
                        onClick={() => setExtractionMode("ocr")}
                        disabled={isLoading}
                      >
                        <span className="text-base font-medium">
                          Documento escaneado
                        </span>
                        <span className="text-sm text-muted-foreground">
                          Activa OCR para extraer texto a partir de imagenes o
                          escaneos sin texto nativo.
                        </span>
                      </Button>
                    </div>
                  </section>
                  <FileUploader
                    onFileDrop={handleFileProcess}
                    isLoading={isLoading}
                    disabled={extractionMode === null}
                    disabledMessage="Selecciona primero el tipo de documento para habilitar la subida."
                  />
                </>
              ) : (
                <ResultsView
                  originalContent={originalContent}
                  redactedContent={redactedContent}
                  detectionStats={detectionStats}
                  fileName={file.name}
                  fileType={file.type}
                  fileSize={file.size}
                  strategy={strategy}
                  extractionMode={extractionMode}
                  progressData={processingProgress}
                  onReset={handleReset}
                  isLoading={isLoading}
                />
              )}
            </div>
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
