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
    name: "Credit Card Numbers",
    description: "Detects and redacts credit card numbers.",
  },
  {
    id: "email",
    name: "Email Addresses",
    description: "Detects and redacts email addresses.",
  },
  {
    id: "phone",
    name: "Phone Numbers",
    description: "Detects and redacts phone numbers.",
  },
  {
    id: "name",
    name: "Names",
    description:
      "Detects and redacts common names (e.g., John Doe).",
  },
  {
    id: "ipAddress",
    name: "IP Addresses",
    description: "Detects and redacts IPv4 and IPv6 addresses.",
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
        <h3 className="font-medium text-lg">Redaction Rules</h3>
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
        <h3 className="font-medium text-lg">Text Redaction Strategy</h3>
        <p className="text-sm text-muted-foreground">
          Choose how to replace sensitive text. This does not apply to PDFs.
        </p>
        <RadioGroup
          value={strategy}
          onValueChange={(value) => onStrategyChange(value as RedactionStrategy)}
          disabled={isPdf}
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="redact" id="redact" />
            <Label htmlFor="redact">Tokenize</Label>
          </div>
          <p className="text-xs text-muted-foreground pl-6">
            Replace with a token, e.g., "[EMAIL]".
          </p>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="mask" id="mask" />
            <Label htmlFor="mask">Mask</Label>
          </div>
          <p className="text-xs text-muted-foreground pl-6">
            Replace with 'x' to preserve length.
          </p>
        </RadioGroup>
      </div>
    </div>
  );
}
