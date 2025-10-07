import { ShieldCheck } from "lucide-react";

export function AppHeader() {
  return (
    <header className="flex items-center gap-3 py-4 px-4 sm:px-6 sticky top-0 bg-background/80 backdrop-blur-sm z-10 border-b">
      <ShieldCheck className="w-8 h-8 text-primary" />
      <h1 className="text-2xl font-headline font-bold tracking-tight text-foreground">
        Aplicación de Privacidad
      </h1>
    </header>
  );
}
