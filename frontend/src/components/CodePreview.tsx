import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { oneDark } from "@codemirror/theme-one-dark";

interface Props {
  code: string;
}

export default function CodePreview({ code }: Props) {
  return (
    <div className="overflow-hidden rounded-xl">
      <CodeMirror
        value={code}
        extensions={[python()]}
        theme={oneDark}
        height="520px"
        readOnly
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          highlightActiveLine: true,
        }}
      />
    </div>
  );
}
