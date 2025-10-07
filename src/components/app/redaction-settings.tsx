"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import type {
  RedactionRule,
  RedactionRules,
  RedactionStrategy,
} from "@/lib/types";

interface RedactionSettingsProps {
  rules: RedactionRules;
  onRuleChange: (ruleId: keyof RedactionRules, enabled: boolean) => void;
  strategy: RedactionStrategy;
  onStrategyChange: (strategy: RedactionStrategy) => void;
  isPdf: boolean;
}

export const ALL_RULES: RedactionRule[] = [
  {
    id: "creditCard",
    name: "Números de Tarjeta de Crédito",
    description: "Detecta y redacta números de tarjetas de crédito.",
  },
  {
    id: "email",
    name: "Direcciones de Correo Electrónico",
    description: "Detecta y redacta direcciones de correo electrónico.",
  },
  {
    id: "phone",
    name: "Números de Teléfono",
    description: "Detecta y redacta números de teléfono.",
  },
  {
    id: "name",
    name: "Nombres",
    description:
      "Detecta y redacta nombres comunes (p. ej., Juan Pérez).",
  },
  {
    id: "ipAddress",
    name: "Direcciones IP",
    description: "Detecta y redacta direcciones IPv4 e IPv6.",
  },
];

export function RedactionSettings({
  rules,
  onRuleChange,
  strategy,
  onStrategyChange,
  isPdf,
}: RedactionSettingsProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h3 className="font-medium text-lg">Reglas de Redacción</h3>
        <div className="space-y-3">
          {ALL_RULES.map((rule) => (
            <div
              key={rule.id}
              className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg"
            >
              <div className="flex-1 pr-4">
                <Label htmlFor={rule.id} className="font-medium">
                  {rule.name}
                </Label>
                <p className="text-xs text-muted-foreground">
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

      <Separator />

      <div className="space-y-4">
        <h3 className="font-medium text-lg">Estrategia de Redacción de Texto</h3>
        <p className="text-sm text-muted-foreground">
          Elige cómo reemplazar el texto sensible. Esto no se aplica a los PDF.
        </p>
        <RadioGroup
          value={strategy}
          onValueChange={(value) => onStrategyChange(value as RedactionStrategy)}
          disabled={isPdf}
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="redact" id="redact" />
            <Label htmlFor="redact">Tokenizar</Label>
          </div>
          <p className="text-xs text-muted-foreground pl-6">
            Reemplazar con un token, ej., "[EMAIL]".
          </p>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="mask" id="mask" />
            <Label htmlFor="mask">Enmascarar</Label>
          </div>
          <p className="text-xs text-muted-foreground pl-6">
            Reemplazar con 'x' para conservar la longitud.
          </p>
        </RadioGroup>
      </div>
    </div>
  );
}
