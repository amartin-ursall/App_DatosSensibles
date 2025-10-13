"use client";

import { Download, RotateCcw, FileDigit, ShieldCheck, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileTypeIcon } from "./icons";
import { LoadingAnimation } from "./loading-animation";
import { useEffect, useState } from "react";


interface ResultsViewProps {
  originalContent: string | null;
  redactedContent: string | Blob | null;
  detectionStats: { total: number; byType: Record<string, number> } | null;
  fileName: string;
  fileType: string;
  strategy: string;
  onReset: () => void;
  isLoading: boolean;
}

const LoadingState = ({ fileName, fileType }: { fileName: string; fileType: string }) => (
  <LoadingAnimation fileName={fileName} fileType={fileType} />
);

const getTypeLabel = (type: string): string => {
  const typeLabels: Record<string, string> = {
    // Financieros
    creditCard: "Tarjetas de Crédito/Débito",
    iban: "IBAN",

    // Identificación oficial
    dni: "DNI Español",
    nie: "NIE Español",
    cif: "CIF Español",
    ssn: "SSN (Seguro Social USA)",
    passport: "Pasaportes",

    // Contacto
    email: "Correos Electrónicos",
    phone: "Teléfonos",
    address: "Direcciones Postales",

    // Fechas y nombres
    dateOfBirth: "Fechas de Nacimiento",
    fullName: "Nombres Completos",
    accountHolder: "Titulares de Cuenta",

    // Usuario y sesión
    username: "Usuarios/Alias",
    cookie: "Cookies/Sesiones",

    // Vehículos
    licensePlate: "Matrículas",

    // Crítico
    credentials: "Credenciales (CRÍTICO)",
    healthData: "Datos de Salud (CRÍTICO)",

    // Otros (legacy)
    license: "Licencias",
    postalAddress: "Direcciones",
    vehiclePlate: "Matrículas",
    ipAddress: "Direcciones IP",
    name: "Nombres",
    rfc: "RFC",
    rut: "RUT",
    cuit: "CUIT/CUIL",
    curp: "CURP",
  };
  return typeLabels[type] || type.toUpperCase();
};

// Función para renderizar texto con redacción (negro sólido)
const renderTextWithRedaction = (text: string) => {
  // Buscar patrones de subrayado __texto__
  const parts = text.split(/(__.+?__)/g);

  return parts.map((part, index) => {
    if (part.startsWith('__') && part.endsWith('__')) {
      // Es texto redactado, remover los __ y aplicar estilo negro sólido
      const redactedText = part.slice(2, -2);
      return (
        <span
          key={index}
          className="bg-black text-black px-1 rounded select-none"
          title="Dato sensible redactado"
        >
          {redactedText}
        </span>
      );
    }
    // Es texto normal
    return part;
  });
};

export function ResultsView({
  originalContent,
  redactedContent,
  detectionStats,
  fileName,
  fileType,
  strategy,
  onReset,
  isLoading,
}: ResultsViewProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  useEffect(() => {
    if (redactedContent instanceof Blob && fileType === "application/pdf") {
      const url = URL.createObjectURL(redactedContent);
      setPdfUrl(url);

      return () => {
        URL.revokeObjectURL(url);
        setPdfUrl(null);
      };
    }
  }, [redactedContent, fileType]);

  const handleDownload = () => {
    if (!redactedContent) return;
    const url =
      pdfUrl ||
      URL.createObjectURL(
        redactedContent instanceof Blob
          ? redactedContent
          : new Blob([redactedContent])
      );
    const a = document.createElement("a");
    a.href = url;
    a.download = `redactado-${fileName}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    if (!pdfUrl) {
      URL.revokeObjectURL(url);
    }
  };


  if (isLoading) {
    return <LoadingState fileName={fileName} fileType={fileType} />;
  }

  const isPdf = fileType === "application/pdf";

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <FileTypeIcon
            type={fileType}
            className="w-8 h-8 text-muted-foreground"
          />
          <div>
            <h2 className="text-xl font-semibold">{fileName}</h2>
            <p className="text-sm text-muted-foreground">
              Análisis completo - datos sensibles completamente redactados (bloques negros).
            </p>
          </div>
        </div>
        <div className="flex gap-2">
        <Button onClick={handleDownload} variant="secondary">
            <Download className="mr-2 h-4 w-4" />
            Descargar
          </Button>
        <Button onClick={onReset} variant="outline">
          <RotateCcw className="mr-2 h-4 w-4" />
          Procesar Otro Archivo
        </Button>
        </div>
      </div>

      {/* Estadísticas de detección */}
      {detectionStats && (
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-blue-500" />
                <CardTitle>Estadísticas de Detección</CardTitle>
              </div>
              <Badge variant={detectionStats.total > 0 ? "destructive" : "default"} className="text-lg px-4 py-1">
                {detectionStats.total} dato{detectionStats.total !== 1 ? "s" : ""} sensible{detectionStats.total !== 1 ? "s" : ""}
              </Badge>
            </div>
            <CardDescription>
              {detectionStats.total > 0
                ? "Se detectaron y redactaron (bloques negros) los siguientes tipos de datos sensibles:"
                : "No se detectaron datos sensibles en este archivo."}
            </CardDescription>
          </CardHeader>
          {detectionStats.total > 0 && (
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {Object.entries(detectionStats.byType)
                  .sort(([, a], [, b]) => b - a)
                  .map(([type, count]) => (
                    <div
                      key={type}
                      className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-lg"
                    >
                      <AlertCircle className="h-4 w-4 text-destructive" />
                      <span className="font-medium">{getTypeLabel(type)}:</span>
                      <Badge variant="secondary">{count}</Badge>
                    </div>
                  ))}
              </div>
            </CardContent>
          )}
        </Card>
      )}

      <div
        className={
          isPdf
            ? ""
            : "grid grid-cols-1 md:grid-cols-2 gap-6 items-start"
        }
      >
        {isPdf ? (
          <Card>
            <CardHeader>
              <CardTitle>Vista Previa del PDF Redactado</CardTitle>
              <CardDescription>
                Los datos sensibles de tu PDF han sido completamente ocultados con bloques negros sólidos.
              </CardDescription>
            </CardHeader>
            <CardContent>
                {pdfUrl ? (
                  <iframe
                    src={pdfUrl}
                    className="w-full h-[600px] rounded-md border"
                    title="Vista Previa del PDF Redactado"
                  ></iframe>
                ) : (
                  <div className="flex flex-col items-center justify-center p-8 bg-secondary rounded-lg text-center h-[600px]">
                     <FileDigit className="w-16 h-16 text-primary mb-4" />
                     <p className="text-lg font-medium">Generando vista previa del PDF...</p>
                  </div>
                )}
            </CardContent>
          </Card>
        ) : (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Original</CardTitle>
              </CardHeader>
              <Separator />
              <CardContent className="p-0">
                <ScrollArea className="h-96">
                  <pre className="p-4 font-code text-sm whitespace-pre-wrap break-all">
                    <code>{originalContent}</code>
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Con Redacción (Negro Sólido)</CardTitle>
                <CardDescription>
                  Los datos sensibles están completamente ocultos con bloques negros
                </CardDescription>
              </CardHeader>
              <Separator />
              <CardContent className="p-0">
                <ScrollArea className="h-96">
                  <pre className="p-4 font-code text-sm whitespace-pre-wrap break-all">
                    <code>{renderTextWithRedaction(redactedContent as string)}</code>
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
