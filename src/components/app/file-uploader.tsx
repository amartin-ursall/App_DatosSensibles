"use client";

import { useState, useCallback, ChangeEvent, DragEvent } from "react";
import { UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { FileTypeIcon } from "./icons";
import { supportedFileTypes } from "@/lib/types";

interface FileUploaderProps {
  onFileDrop: (file: File) => void;
  isLoading: boolean;
}

export function FileUploader({ onFileDrop, isLoading }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (file: File | null) => {
    if (file) {
      // Simulate upload progress
      setUploadProgress(0);
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 95) {
            clearInterval(interval);
            return prev;
          }
          return prev + 5;
        });
      }, 50);

      onFileDrop(file);
    }
  };

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
      e.dataTransfer.clearData();
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    document.getElementById("file-input")?.click();
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Card
        className={cn(
          "transition-all duration-300",
          isDragging && "border-primary ring-2 ring-primary ring-offset-2",
          isLoading && "pointer-events-none opacity-50"
        )}
      >
        <CardContent
          className="p-0"
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center p-8 sm:p-12 text-center">
            <div className="p-4 bg-secondary rounded-full mb-4">
              <UploadCloud className="w-10 h-10 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">
              Arrastra y suelta archivos aquí
            </h3>
            <p className="text-muted-foreground mb-4">
              o haz clic para subir un archivo
            </p>
            <input
              id="file-input"
              type="file"
              className="hidden"
              onChange={handleInputChange}
              accept={supportedFileTypes.join(",")}
            />
            <Button onClick={triggerFileInput} disabled={isLoading}>
              Buscar Archivos
            </Button>
            <p className="text-xs text-muted-foreground mt-4">
              Tipos de archivo soportados: .txt, .csv, .md, .json, .log, .pdf
            </p>
          </div>
        </CardContent>
      </Card>
      {isLoading && (
        <div className="mt-4">
          <Progress value={uploadProgress} className="w-full" />
          <p className="text-sm text-center mt-2 text-muted-foreground animate-pulse">
            Procesando tu archivo...
          </p>
        </div>
      )}
    </div>
  );
}
