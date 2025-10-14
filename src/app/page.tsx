"use client";

import { useCallback, useState } from "react";
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
  const { toast } = useToast();

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

      setIsLoading(true);
      setFile(uploadedFile);
      setOriginalContent(null);
      setRedactedContent(null);
      setDetectionStats(null);

      try {
        if (uploadedFile.type === "application/pdf") {
          // Procesar PDF en el backend Python
          const formData = new FormData();
          formData.append('file', uploadedFile);
          formData.append('rules', JSON.stringify(rules));
          formData.append('sensitivityLevel', sensitivityLevel);
          formData.append('action', 'highlight'); // Siempre subrayar

          // Usar backend Python (puerto 5000)
          const response = await fetch('http://localhost:5000/api/process-pdf', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Error al procesar PDF en el backend Python');
          }

          const pdfBlob = await response.blob();
          const totalMatches = parseInt(response.headers.get('X-Total-Matches') || '0');
          const matchesByType = JSON.parse(response.headers.get('X-Matches-By-Type') || '{}');

          setRedactedContent(pdfBlob);
          setDetectionStats({
            total: totalMatches,
            byType: matchesByType,
          });

          toast({
            title: "PDF procesado con backend Python",
            description: `Se detectaron ${totalMatches} dato(s) sensible(s).`,
          });
        } else {
          const text = await uploadedFile.text();
          setOriginalContent(text);

          // Usar backend Python para detección en texto
          const response = await fetch('http://localhost:5000/api/detect-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text,
              rules,
              sensitivityLevel,
            }),
          });

          if (!response.ok) {
            throw new Error('Error al detectar texto en el backend Python');
          }

          const data = await response.json();
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
        console.error("Error processing file:", error);
        toast({
          variant: "destructive",
          title: "Error de Procesamiento",
          description: "Hubo un error al procesar tu archivo. El PDF podría estar malformado o encriptado.",
        });
        handleReset();
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, rules, strategy, sensitivityLevel, toast]
  );

  const handleReset = () => {
    setFile(null);
    setOriginalContent(null);
    setRedactedContent(null);
    setDetectionStats(null);
    setIsLoading(false);
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
                <FileUploader
                  onFileDrop={handleFileProcess}
                  isLoading={isLoading}
                />
              ) : (
                <ResultsView
                  originalContent={originalContent}
                  redactedContent={redactedContent}
                  detectionStats={detectionStats}
                  fileName={file.name}
                  fileType={file.type}
                  strategy={strategy}
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
