import React from "react";
import { AlertTriangle, Info } from "lucide-react";

export const DisclaimerBanner: React.FC = () => {
  return (
    <div className="bg-amber-950/40 border-b border-amber-900/40 px-4 py-2.5 text-xs text-amber-200/90">
      <div className="max-w-7xl mx-auto flex items-start gap-2.5">
        <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-amber-300">Mandatory Statutory Notice: </span>
          NyayaSaathi AI (न्यायसाथी AI) is an informational legal technology assistant based on official Indian consumer statutes and government guidance.
          Generated materials do not constitute formal legal representation, advocacy, or binding determinations of liability under the Advocates Act, 1961. For active litigation, consult an enrolled legal practitioner or National Consumer Helpline (1915).
        </div>
      </div>
    </div>
  );
};
