"use client";

import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { ShieldCheck } from "lucide-react";
import type {
  RedactionRule,
  RedactionRules,
} from "@/lib/types";

interface RedactionSettingsProps {
  rules: RedactionRules;
  onRuleChange: (ruleId: keyof RedactionRules, enabled: boolean) => void;
  isPdf: boolean;
}

export const ALL_RULES: RedactionRule[] = [
  // Financieros (ALTO riesgo)
  {
    id: "creditCard",
    name: "Tarjetas de Crédito/Débito",
    description: "Detecta números de tarjetas con validación Luhn.",
  },
  {
    id: "iban",
    name: "IBAN (con puntos y espacios)",
    description: "Detecta cuentas bancarias IBAN con validación módulo 97.",
  },

  // Identificación oficial (ALTO riesgo)
  {
    id: "dni",
    name: "DNI Español",
    description: "Detecta DNI con validación de letra de control.",
  },
  {
    id: "nie",
    name: "NIE Español",
    description: "Detecta NIE con validación de letra de control.",
  },
  {
    id: "cif",
    name: "CIF Español",
    description: "Detecta CIF de empresas con validación.",
  },
  {
    id: "ssn",
    name: "SSN / Número de Seguridad Social",
    description: "Detecta números de Seguro Social (USA y otros países).",
  },
  {
    id: "employeeId",
    name: "Employee ID / ID de Empleado",
    description: "Detecta identificadores de empleado (EMP-1234, ID: 5678, etc.).",
  },
  {
    id: "passport",
    name: "Números de Pasaporte",
    description: "Detecta pasaportes en múltiples formatos internacionales.",
  },

  // Contacto (MEDIO riesgo)
  {
    id: "email",
    name: "Correos Electrónicos",
    description: "Detecta emails con validación RFC compliant.",
  },
  {
    id: "phone",
    name: "Números de Teléfono",
    description: "Detecta teléfonos españoles e internacionales.",
  },
  {
    id: "address",
    name: "Direcciones Postales",
    description: "Detecta direcciones en múltiples formatos (calle, número, CP, etc.).",
  },

  // Fechas y nombres (MEDIO-ALTO riesgo)
  {
    id: "dateOfBirth",
    name: "Fechas de Nacimiento",
    description: "Detecta fechas en múltiples formatos (DD/MM/YYYY, 1 de enero de 1990, etc.).",
  },
  {
    id: "fullName",
    name: "Nombres Completos",
    description: "Detecta nombres y apellidos con títulos (Sr., Dr., etc.).",
  },
  {
    id: "accountHolder",
    name: "Titulares de Cuenta",
    description: "Detecta titulares, beneficiarios y propietarios.",
  },

  // Usuario y sesión (MEDIO riesgo)
  {
    id: "username",
    name: "Nombres de Usuario y Alias",
    description: "Detecta @usuarios, usernames, logins y alias.",
  },
  {
    id: "cookie",
    name: "Cookies y Sesiones Web",
    description: "Detecta cookies, tokens JWT, sessionID y headers Set-Cookie.",
  },

  // Vehículos (MEDIO riesgo)
  {
    id: "licensePlate",
    name: "Matrículas de Vehículos",
    description: "Detecta matrículas españolas y otros formatos internacionales.",
  },

  // CRÍTICO (máximo riesgo RGPD)
  {
    id: "credentials",
    name: "Credenciales y Contraseñas (CRÍTICO)",
    description: "Detecta contraseñas, API keys, tokens y secretos.",
  },
  {
    id: "healthData",
    name: "Datos de Salud (CRÍTICO)",
    description: "Detecta diagnósticos, medicación, historias clínicas.",
  },
];

export function RedactionSettings({
  rules,
  onRuleChange,
  isPdf,
}: RedactionSettingsProps) {
  const enabledCount = Object.values(rules).filter(Boolean).length;

  const toggleAll = (enabled: boolean) => {
    ALL_RULES.forEach((rule) => {
      onRuleChange(rule.id, enabled);
    });
  };

  return (
    <div className="space-y-6">
      {/* Modo de detección estricto siempre activo */}
      <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-blue-500" />
          <div>
            <h3 className="font-medium text-sm">Modo Estricto Activo</h3>
            <p className="text-xs text-muted-foreground">
              Máxima detección de datos sensibles
            </p>
          </div>
        </div>
      </div>

      <Separator />

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-lg">Reglas de Redacción</h3>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-8 px-2 text-xs flex-1"
            onClick={() => toggleAll(true)}
          >
            Activar todas
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-8 px-2 text-xs flex-1"
            onClick={() => toggleAll(false)}
          >
            Desactivar todas
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          {enabledCount} de {ALL_RULES.length} reglas activas
        </p>
        <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2">
          {ALL_RULES.map((rule) => (
            <div
              key={rule.id}
              className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg hover:bg-secondary/70 transition-colors"
            >
              <div className="flex-1 pr-4">
                <Label htmlFor={rule.id} className="font-medium cursor-pointer text-sm">
                  {rule.name}
                </Label>
                <p className="text-xs text-muted-foreground mt-1">
                  {rule.description}
                </p>
              </div>
              <Switch
                id={rule.id}
                checked={rules[rule.id]}
                onCheckedChange={(checked) => onRuleChange(rule.id, checked)}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
