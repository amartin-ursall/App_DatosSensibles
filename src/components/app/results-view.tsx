"use client";

import { Download, RotateCcw, FileDigit } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileTypeIcon } from "./icons";
import { Skeleton } from "../ui/skeleton";
import { useEffect, useState } from "react";


interface ResultsViewProps {
  originalContent: string | null;
  redactedContent: string | Blob | null;
  fileName: string;
  fileType: string;
  onReset: () => void;
  isLoading: boolean;
}

const LoadingState = () => (
  <div className="space-y-4">
    <Skeleton className="h-8 w-1/3" />
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-1/4" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-1/4" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    </div>
  </div>
);

export function ResultsView({
  originalContent,
  redactedContent,
  fileName,
  fileType,
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
    a.download = `redacted-${fileName}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    if (!pdfUrl) {
      URL.revokeObjectURL(url);
    }
  };


  if (isLoading) {
    return <LoadingState />;
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
              Redaction complete.
            </p>
          </div>
        </div>
        <div className="flex gap-2">
        <Button onClick={handleDownload} variant="secondary">
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
        <Button onClick={onReset} variant="outline">
          <RotateCcw className="mr-2 h-4 w-4" />
          Process Another File
        </Button>
        </div>
      </div>

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
              <CardTitle>Redacted PDF Preview</CardTitle>
              <CardDescription>
                Sensitive content in your PDF has been blacked out.
              </CardDescription>
            </CardHeader>
            <CardContent>
                {pdfUrl ? (
                  <iframe
                    src={pdfUrl}
                    className="w-full h-[600px] rounded-md border"
                    title="Redacted PDF Preview"
                  ></iframe>
                ) : (
                  <div className="flex flex-col items-center justify-center p-8 bg-secondary rounded-lg text-center h-[600px]">
                     <FileDigit className="w-16 h-16 text-primary mb-4" />
                     <p className="text-lg font-medium">Generating PDF preview...</p>
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
                <CardTitle>Redacted</CardTitle>
              </CardHeader>
              <Separator />
              <CardContent className="p-0">
                <ScrollArea className="h-96">
                  <pre className="p-4 font-code text-sm whitespace-pre-wrap break-all">
                    <code>{redactedContent as string}</code>
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
