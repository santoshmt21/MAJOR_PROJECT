import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MarkdownMessage({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p style={{ margin: "0 0 10px" }}>{children}</p>,
        h1: ({ children }) => <h1 style={{ fontSize: 20, margin: "0 0 10px", color: "#1B4332" }}>{children}</h1>,
        h2: ({ children }) => <h2 style={{ fontSize: 18, margin: "0 0 10px", color: "#1B4332" }}>{children}</h2>,
        h3: ({ children }) => <h3 style={{ fontSize: 16, margin: "0 0 8px", color: "#1B4332" }}>{children}</h3>,
        ul: ({ children }) => <ul style={{ margin: "6px 0 10px", paddingLeft: 20 }}>{children}</ul>,
        ol: ({ children }) => <ol style={{ margin: "6px 0 10px", paddingLeft: 20 }}>{children}</ol>,
        li: ({ children }) => <li style={{ marginBottom: 4 }}>{children}</li>,
        blockquote: ({ children }) => <blockquote style={{ borderLeft: "3px solid #D4831A", margin: "8px 0", paddingLeft: 12, color: "#52796F" }}>{children}</blockquote>,
        table: ({ children }) => <div style={{ overflowX: "auto", margin: "10px 0" }}><table style={{ borderCollapse: "collapse", minWidth: "100%", fontSize: 13 }}>{children}</table></div>,
        th: ({ children }) => <th style={{ background: "#EEF5EE", border: "1px solid #D7E4DA", padding: "7px 9px", textAlign: "left", fontWeight: 700 }}>{children}</th>,
        td: ({ children }) => <td style={{ border: "1px solid #E8E0D5", padding: "7px 9px", verticalAlign: "top" }}>{children}</td>,
        code: ({ children }) => <code style={{ background: "#F3F4F6", borderRadius: 4, padding: "2px 5px", fontSize: 12 }}>{children}</code>
      }}
    >
      {content.replace(/<br\s*\/?>/gi, "\n")}
    </ReactMarkdown>
  );
}
