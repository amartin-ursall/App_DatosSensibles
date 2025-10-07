import {
  FileText,
  FileJson,
  FileCode2,
  FileTerminal,
  FileDigit,
  FileSymlink,
} from "lucide-react";
import type { LucideProps } from "lucide-react";
import type { FC } from "react";

export const FileTypeIcon: FC<
  { type: string | undefined } & LucideProps
> = ({ type, ...props }) => {
  if (!type) return <FileSymlink {...props} />;
  if (type.includes("pdf")) return <FileDigit {...props} />;
  if (type.includes("json")) return <FileJson {...props} />;
  if (type.includes("csv")) return <FileCode2 {...props} />;
  if (type.includes("markdown")) return <FileText {...props} />;
  if (type.includes("log")) return <FileTerminal {...props} />;

  return <FileText {...props} />;
};
