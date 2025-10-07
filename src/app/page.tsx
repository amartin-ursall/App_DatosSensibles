"use client";

import { useCallback, useState } from "react";
import {
  SidebarProvider,
  Sidebar,
  SidebarInset,
  SidebarHeader,
  SidebarContent,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { AppHeader } from "@/components/app/app-header";
import {
  RedactionRules,
  RedactionStrategy,
  supportedFileTypes,
} from "@/lib/types";
import { ALL_RULES, RedactionSettings } from "@/components/app/redaction-settings";
import { FileUploader } from "@/components/app/file-uploader";
import { useToast } from "@/hooks/use-toast";
import { redactPdf, redactText } from "@/lib/redact";
import { ResultsView } from "@/components/app/results-view";
import { Button } from "@/components/ui/button";

export default function PrivacyPalPage() {
  const [file, setFile] = useState<File | null>(null);
  const [originalContent, setOriginalContent] = useState<string | null>(null);
  const [redactedContent, setRedactedContent] = useState<string | Blob | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const [rules, setRules] = useState<RedactionRules>(() =>
    ALL_RULES.reduce(
      (acc, rule) => ({ ...acc, [rule.id]: true }),
      {} as RedactionRules
    )
  );
  const [strategy, setStrategy] = useState<RedactionStrategy>("redact");

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
          title: "Unsupported File Type",
          description: `Sorry, we do not support "${
            uploadedFile.name.split(".").pop() || "unknown"
          }" files.`,
        });
        return;
      }

      setIsLoading(true);
      setFile(uploadedFile);
      setOriginalContent(null);
      setRedactedContent(null);

      try {
        if (uploadedFile.type === "application/pdf") {
          const redactedPdfBlob = await redactPdf(uploadedFile, rules);
          setRedactedContent(redactedPdfBlob);
        } else {
          const text = await uploadedFile.text();
          setOriginalContent(text);
          const redactedText = redactText(text, rules, strategy);
          setRedactedContent(redactedText);
        }
        toast({
          title: "File processed",
          description: "Your file has been redacted successfully.",
        });
      } catch (error) {
        console.error("Error processing file:", error);
        toast({
          variant: "destructive",
          title: "Processing Error",
          description: "There was an error processing your file. The PDF might be malformed or encrypted.",
        });
        handleReset();
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, rules, strategy, toast]
  );

  const handleReset = () => {
    setFile(null);
    setOriginalContent(null);
    setRedactedContent(null);
    setIsLoading(false);
  };

  return (
    <SidebarProvider>
      <div className="flex min-h-screen">
        <Sidebar collapsible="icon" className="p-0">
          <SidebarHeader className="p-4 border-b">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-lg">Settings</h2>
              <div className="md:hidden">
                <SidebarTrigger />
              </div>
            </div>
          </SidebarHeader>
          <SidebarContent className="p-4">
            <RedactionSettings
              rules={rules}
              onRuleChange={handleRuleChange}
              strategy={strategy}
              onStrategyChange={setStrategy}
              isPdf={file?.type === "application/pdf"}
            />
          </SidebarContent>
        </Sidebar>
        <SidebarInset className="bg-background">
          <AppHeader />
          <main className="flex flex-1 flex-col justify-center items-center p-4 sm:p-6 pb-8">
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
                  fileName={file.name}
                  fileType={file.type}
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
