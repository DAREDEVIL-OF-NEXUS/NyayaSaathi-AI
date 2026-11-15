"use client";

import React, { useState } from "react";
import { Copy, Check, ExternalLink, Bookmark } from "lucide-react";

interface FormattedLegalResponseProps {
  content: string;
  className?: string;
  showCopyButton?: boolean;
}

export const FormattedLegalResponse: React.FC<FormattedLegalResponseProps> = ({
  content,
  className = "",
  showCopyButton = true,
}) => {
  const [copied, setCopied] = useState(false);

  if (!content) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to parse inline markdown (bold, code, links)
  const renderInline = (text: string) => {
    // Split by code blocks first
    const codeParts = text.split(/(`[^`]+`)/g);

    return codeParts.map((part, pIdx) => {
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code
            key={pIdx}
            className="px-1.5 py-0.5 mx-0.5 rounded bg-slate-800/90 border border-slate-700/60 text-amber-400 font-mono text-[11px]"
          >
            {part.slice(1, -1)}
          </code>
        );
      }

      // Parse bold **text**
      const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
      return boldParts.map((bPart, bIdx) => {
        if (bPart.startsWith("**") && bPart.endsWith("**")) {
          const inner = bPart.slice(2, -2);
          // Highlight statutory terms distinctly
          const isStatutory = /section|rule|act|consumer|commission|court|guideline|clause/i.test(inner);
          return (
            <strong
              key={`${pIdx}-${bIdx}`}
              className={isStatutory ? "text-amber-300 font-semibold" : "text-slate-100 font-semibold"}
            >
              {inner}
            </strong>
          );
        }

        // Parse italics *text*
        const italicParts = bPart.split(/(\*[^*]+\*)/g);
        return italicParts.map((iPart, iIdx) => {
          if (iPart.startsWith("*") && iPart.endsWith("*") && !iPart.startsWith("**")) {
            return (
              <em key={`${pIdx}-${bIdx}-${iIdx}`} className="text-slate-300 italic">
                {iPart.slice(1, -1)}
              </em>
            );
          }
          return iPart;
        });
      });
    });
  };

  // Split into structural blocks (headers, lists, blockquotes, paragraphs)
  const lines = content.split("\n");
  const blocks: React.ReactNode[] = [];
  let currentList: { type: "bullet" | "number"; items: string[] } | null = null;

  const flushList = () => {
    if (!currentList) return;
    if (currentList.type === "bullet") {
      blocks.push(
        <ul key={`list-${blocks.length}`} className="my-2.5 space-y-1.5 pl-1">
          {currentList.items.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-200 leading-relaxed">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-400 shrink-0 mt-2" />
              <div className="flex-1">{renderInline(item)}</div>
            </li>
          ))}
        </ul>
      );
    } else {
      blocks.push(
        <ol key={`list-${blocks.length}`} className="my-2.5 space-y-1.5 pl-1">
          {currentList.items.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-200 leading-relaxed">
              <span className="h-4 w-4 rounded-full bg-amber-500/20 text-amber-400 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5 border border-amber-500/30">
                {idx + 1}
              </span>
              <div className="flex-1">{renderInline(item)}</div>
            </li>
          ))}
        </ol>
      );
    }
    currentList = null;
  };

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (!trimmed) {
      flushList();
      continue;
    }

    // Header 3: ### Heading
    if (trimmed.startsWith("### ")) {
      flushList();
      blocks.push(
        <h4
          key={`h3-${i}`}
          className="text-xs font-bold uppercase tracking-wider text-amber-400 mt-4 mb-2 flex items-center gap-1.5 border-b border-slate-800/80 pb-1"
        >
          <Bookmark className="h-3 w-3 text-amber-500" />
          <span>{trimmed.replace(/^###\s+/, "")}</span>
        </h4>
      );
      continue;
    }

    // Header 2: ## Heading
    if (trimmed.startsWith("## ")) {
      flushList();
      blocks.push(
        <h3
          key={`h2-${i}`}
          className="text-sm font-bold text-slate-100 mt-4 mb-2 border-l-2 border-amber-500 pl-2.5"
        >
          {trimmed.replace(/^##\s+/, "")}
        </h3>
      );
      continue;
    }

    // Header 1: # Heading
    if (trimmed.startsWith("# ")) {
      flushList();
      blocks.push(
        <h2
          key={`h1-${i}`}
          className="text-base font-extrabold text-amber-300 mt-4 mb-2"
        >
          {trimmed.replace(/^#\s+/, "")}
        </h2>
      );
      continue;
    }

    // Bullet item: - or *
    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      const itemText = trimmed.replace(/^[-*]\s+/, "");
      if (currentList && currentList.type === "bullet") {
        currentList.items.push(itemText);
      } else {
        flushList();
        currentList = { type: "bullet", items: [itemText] };
      }
      continue;
    }

    // Numbered item: 1. or 2.
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      const itemText = numMatch[2];
      if (currentList && currentList.type === "number") {
        currentList.items.push(itemText);
      } else {
        flushList();
        currentList = { type: "number", items: [itemText] };
      }
      continue;
    }

    // Blockquote: > text
    if (trimmed.startsWith("> ")) {
      flushList();
      blocks.push(
        <blockquote
          key={`quote-${i}`}
          className="my-2 p-3 rounded-xl bg-slate-900/90 border-l-2 border-amber-500 text-xs text-amber-200/90 italic"
        >
          {renderInline(trimmed.replace(/^>\s+/, ""))}
        </blockquote>
      );
      continue;
    }

    // Normal paragraph
    flushList();
    blocks.push(
      <p key={`p-${i}`} className="my-1.5 text-xs text-slate-200 leading-relaxed font-normal">
        {renderInline(trimmed)}
      </p>
    );
  }

  flushList();

  return (
    <div className={`relative group/output ${className}`}>
      {showCopyButton && (
        <button
          onClick={handleCopy}
          title="Copy formatted answer"
          className="absolute -top-1 right-0 opacity-0 group-hover/output:opacity-100 transition-opacity p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 text-xs flex items-center gap-1 border border-slate-700 shadow-sm"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-emerald-400" />
              <span className="text-[10px] text-emerald-400 font-medium">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span className="text-[10px]">Copy</span>
            </>
          )}
        </button>
      )}

      <div className="space-y-1 font-sans">{blocks}</div>
    </div>
  );
};
