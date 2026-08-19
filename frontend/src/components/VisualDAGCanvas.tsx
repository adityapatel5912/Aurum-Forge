import { useMemo, useRef, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Download,
  Eye,
  Image as ImageIcon,
  Maximize2,
  Minimize2,
  Move,
  Play,
  Sparkles,
  Zap,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import type { Dag, DagTask } from "../types";

interface Props {
  dag: Dag;
  goal?: string;
  onExecuteNode?: (taskId: string) => void;
}

interface ProcessedNode {
  id: string;
  task: DagTask;
  category: "trigger" | "process" | "output";
  level: number;
  colIndex: number;
  x: number;
  y: number;
}

function getNodeCategory(task: DagTask): "trigger" | "process" | "output" {
  const meta = (task as { category?: string }).category;
  if (meta === "trigger" || meta === "process" || meta === "output") {
    return meta;
  }
  const tool = task.tool.toLowerCase();
  const source = task.source.toLowerCase();

  if (
    tool.includes("notify") ||
    tool.includes("send") ||
    tool.includes("email") ||
    tool.includes("gmail") ||
    tool.includes("notion") ||
    tool.includes("log") ||
    tool.includes("export") ||
    tool.includes("slack") ||
    source.includes("notion") ||
    source.includes("gmail")
  ) {
    return "output";
  }

  if (
    tool.includes("trigger") ||
    tool.includes("goal") ||
    tool.includes("voice") ||
    tool.includes("webhook") ||
    tool.includes("start")
  ) {
    return "trigger";
  }

  return "process";
}

export default function VisualDAGCanvas({ dag, goal, onExecuteNode }: Props) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const svgRef = useRef<SVGSVGElement>(null);
  const dragState = useRef<{ startX: number; startY: number; baseX: number; baseY: number; moved: boolean } | null>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    dragState.current = {
      startX: e.clientX,
      startY: e.clientY,
      baseX: pan.x,
      baseY: pan.y,
      moved: false,
    };
    setIsDragging(true);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    const st = dragState.current;
    if (!st) return;
    const dx = e.clientX - st.startX;
    const dy = e.clientY - st.startY;
    if (Math.abs(dx) + Math.abs(dy) > 3) st.moved = true;
    setPan({ x: st.baseX + dx / zoom, y: st.baseY + dy / zoom });
  };

  const stopDragging = () => {
    dragState.current = null;
    setIsDragging(false);
  };

  const fitView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const serializeSvg = (): string | null => {
    const svg = svgRef.current;
    if (!svg) return null;
    const clone = svg.cloneNode(true) as SVGSVGElement;
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    clone.style.transform = "";
    clone.style.transition = "";
    return new XMLSerializer().serializeToString(clone);
  };

  const exportSvg = () => {
    const data = serializeSvg();
    if (!data) return;
    const blob = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "forge-dag.svg";
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportPng = () => {
    const data = serializeSvg();
    if (!data) return;
    const img = new Image();
    const svgUrl = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(data);
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = 1600;
      canvas.height = Math.round((1600 * (img.height || 900)) / (img.width || 1600)) || 900;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.fillStyle = "#FFFBF0";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const a = document.createElement("a");
        a.href = canvas.toDataURL("image/png");
        a.download = "forge-dag.png";
        a.click();
      }
    };
    img.src = svgUrl;
  };

  // Compute node positions & topological leveling
  const { nodes, edges, maxLevel, width, height } = useMemo(() => {
    const ids = Object.keys(dag);
    if (!ids.length) {
      return { nodes: [], edges: [], maxLevel: 0, width: 600, height: 350 };
    }

    // Topological sort
    const done = new Set<string>();
    const levels: string[][] = [];
    let remaining = new Set(ids);
    while (remaining.size) {
      const ready = [...remaining].filter((id) =>
        (dag[id].deps ?? []).every((d) => done.has(d) || !(d in dag))
      );
      const level = ready.length ? ready : [...remaining];
      levels.push(level);
      level.forEach((id) => done.add(id));
      remaining = new Set([...remaining].filter((id) => !done.has(id)));
    }

    const nodeWidth = 200;
    const nodeHeight = 85;
    const gapX = 140;
    const gapY = 30;

    const processedNodes: ProcessedNode[] = [];
    const processedEdges: Array<{
      from: ProcessedNode;
      to: ProcessedNode;
      fromId: string;
      toId: string;
      isParallel: boolean;
    }> = [];

    // Layout
    levels.forEach((levelIds, lvlIdx) => {
      const totalLevelHeight = levelIds.length * nodeHeight + (levelIds.length - 1) * gapY;
      const startY = Math.max(40, (360 - totalLevelHeight) / 2);

      levelIds.forEach((id, colIdx) => {
        const task = dag[id];
        const cat = getNodeCategory(task);
        const x = 60 + lvlIdx * (nodeWidth + gapX);
        const y = startY + colIdx * (nodeHeight + gapY);

        processedNodes.push({
          id,
          task,
          category: cat,
          level: lvlIdx,
          colIndex: colIdx,
          x,
          y,
        });
      });
    });

    const nodeMap = new Map(processedNodes.map((n) => [n.id, n]));

    // Generate Edges
    processedNodes.forEach((node) => {
      const deps = node.task.deps || [];
      deps.forEach((depId) => {
        const fromNode = nodeMap.get(depId);
        if (fromNode) {
          processedEdges.push({
            from: fromNode,
            to: node,
            fromId: depId,
            toId: node.id,
            isParallel: Boolean(node.task.parallel),
          });
        }
      });

      // If no explicit deps but at level > 0, link from previous level
      if (!deps.length && node.level > 0) {
        const prevLevelNodes = processedNodes.filter((n) => n.level === node.level - 1);
        prevLevelNodes.forEach((fromNode) => {
          processedEdges.push({
            from: fromNode,
            to: node,
            fromId: fromNode.id,
            toId: node.id,
            isParallel: Boolean(node.task.parallel),
          });
        });
      }
    });

    const canvasWidth = Math.max(750, (levels.length + 1) * (nodeWidth + gapX));
    const canvasHeight = Math.max(400, Math.max(...levels.map((l) => l.length)) * 130 + 100);

    return {
      nodes: processedNodes,
      edges: processedEdges,
      maxLevel: levels.length,
      width: canvasWidth,
      height: canvasHeight,
    };
  }, [dag]);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  if (!nodes.length) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded-2xl border border-dashed border-navy/20 bg-cream/30 p-6 text-center">
        <Sparkles className="h-8 w-8 text-gold/60 mb-2" />
        <p className="font-display text-sm font-bold text-navy/70">No Workflow DAG Planned</p>
        <p className="text-xs text-navy/40 mt-1">
          Add sites or official MCPs to generate an interactive visual DAG
        </p>
      </div>
    );
  }

  return (
    <div className="relative flex flex-col overflow-hidden rounded-3xl border border-navy/15 bg-white/90 shadow-card backdrop-blur-md">
      {/* Canvas Toolbar Header */}
      <div className="flex items-center justify-between border-b border-navy/10 bg-cream/40 px-5 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-navy text-gold">
            <Zap className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-display text-xs font-bold uppercase tracking-wider text-navy">
              Visual DAG Canvas
            </h3>
            <p className="text-[11px] text-navy/55">
              {nodes.length} Tasks &bull; {edges.length} Data Flow Edges
            </p>
          </div>
        </div>

        {/* Legend */}
        <div className="hidden sm:flex items-center gap-4 text-[11px] font-bold">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-blue-500 ring-2 ring-blue-200" />
            <span className="text-blue-700">Trigger</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-200" />
            <span className="text-emerald-700">Process</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-purple-500 ring-2 ring-purple-200" />
            <span className="text-purple-700">Output</span>
          </div>
        </div>

        {/* Zoom / Pan / Fit / Export Controls */}
        <div className="flex items-center gap-1 rounded-xl border border-navy/10 bg-white/80 p-1 shadow-sm">
          <button
            onClick={() => setZoom((z) => Math.min(1.6, z + 0.15))}
            className="rounded-lg p-1.5 text-navy/60 hover:bg-navy/5 hover:text-navy"
            title="Zoom In"
          >
            <ZoomIn className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}
            className="rounded-lg p-1.5 text-navy/60 hover:bg-navy/5 hover:text-navy"
            title="Zoom Out"
          >
            <ZoomOut className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={fitView}
            className={`rounded-lg p-1.5 transition ${pan.x === 0 && pan.y === 0 && zoom === 1 ? "text-gold-deep" : "text-navy/60 hover:bg-navy/5 hover:text-navy"}`}
            title="Fit View (reset zoom + pan)"
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </button>
          <span className="font-mono text-[10px] font-bold text-navy/40">{Math.round(zoom * 100)}%</span>
          <div className="mx-0.5 h-4 w-px bg-navy/10" />
          <button
            onClick={exportSvg}
            className="rounded-lg p-1.5 text-navy/60 hover:bg-navy/5 hover:text-navy"
            title="Export DAG as SVG"
          >
            <Download className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={exportPng}
            className="rounded-lg p-1.5 text-navy/60 hover:bg-navy/5 hover:text-navy"
            title="Export DAG as PNG"
          >
            <ImageIcon className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Interactive SVG Canvas (drag to pan) */}
      <div
        className="relative h-[340px] w-full overflow-hidden bg-[radial-gradient(#C6A96B18_1px,transparent_1px)] [background-size:16px_16px]"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={stopDragging}
        onMouseLeave={stopDragging}
      >
        {isDragging && (
          <div className="pointer-events-none absolute right-3 top-3 z-10 flex items-center gap-1 rounded-lg bg-navy/80 px-2 py-1 text-[10px] font-bold text-cream">
            <Move className="h-3 w-3 text-gold" /> Panning…
          </div>
        )}
        <svg
          ref={svgRef}
          className={`h-full w-full select-none ${isDragging ? "cursor-grabbing" : "cursor-grab"} active:cursor-grabbing`}
          viewBox={`0 0 ${width} ${height}`}
          style={{
            transform: `scale(${zoom}) translate(${pan.x}px, ${pan.y}px)`,
            transformOrigin: "center center",
            transition: isDragging ? "none" : "transform 0.15s ease-out",
          }}
        >
          <defs>
            {/* Edge Gradients */}
            <linearGradient id="edge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#10B981" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.8" />
            </linearGradient>

            <linearGradient id="gold-edge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#C6A96B" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#E4D3AC" stopOpacity="1" />
              <stop offset="100%" stopColor="#C6A96B" stopOpacity="0.9" />
            </linearGradient>

            {/* Glowing Drop Filter */}
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>

            <filter id="gold-node-glow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Animated Bezier Edges */}
          {edges.map((edge, i) => {
            const startX = edge.from.x + 200;
            const startY = edge.from.y + 42;
            const endX = edge.to.x;
            const endY = edge.to.y + 42;
            const deltaX = (endX - startX) * 0.55;

            const pathData = `M ${startX} ${startY} C ${startX + deltaX} ${startY}, ${endX - deltaX} ${endY}, ${endX} ${endY}`;

            return (
              <g key={i}>
                {/* Background Shadow Edge */}
                <path
                  d={pathData}
                  fill="none"
                  stroke="#0A1931"
                  strokeOpacity="0.1"
                  strokeWidth="6"
                  strokeLinecap="round"
                />
                {/* Glowing Flow Edge */}
                <path
                  d={pathData}
                  fill="none"
                  stroke="url(#edge-gradient)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  className="animate-pulse"
                />
                {/* Flow particle pulse with Gold Glow */}
                <circle r="4" fill="#C6A96B" filter="url(#glow)">
                  <animateMotion path={pathData} dur={`${2.0 + (i % 3) * 0.4}s`} repeatCount="indefinite" />
                </circle>
              </g>
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            const isSelected = node.id === selectedNodeId;
            const isParallel = Boolean(node.task.parallel);

            // Color themes per category — final Gold outputs pulse in #C6A96B
            const isGoldOutput =
              Boolean((node.task as { gold_pulse?: boolean }).gold_pulse) ||
              (node.task as { color?: string }).color === "#C6A96B";
            const theme = isGoldOutput
              ? {
                  bg: "fill-[#FFFBF0]/95 stroke-[#C6A96B]",
                  badge: "bg-[#C6A96B] text-navy",
                  accent: "#C6A96B",
                  text: "text-[#0A1931]",
                }
              : {
              trigger: {
                bg: "fill-blue-50/95 stroke-blue-500",
                badge: "bg-blue-600 text-white",
                accent: "#3B82F6",
                text: "text-blue-900",
              },
              process: {
                bg: "fill-emerald-50/95 stroke-emerald-500",
                badge: "bg-emerald-600 text-white",
                accent: "#10B981",
                text: "text-emerald-900",
              },
              output: {
                bg: "fill-purple-50/95 stroke-purple-500",
                badge: "bg-purple-600 text-white",
                accent: "#8B5CF6",
                text: "text-purple-900",
              },
            }[node.category];

            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                onClick={() => setSelectedNodeId(node.id === selectedNodeId ? null : node.id)}
                className="cursor-pointer transition-transform hover:scale-[1.03]"
              >
                {/* Outer Aurum Gold Pulse Ring */}
                <rect
                  width="204"
                  height="88"
                  x="-2"
                  y="-2"
                  rx="18"
                  fill="none"
                  stroke="#C6A96B"
                  strokeWidth="1.5"
                  strokeOpacity="0.7"
                  filter="url(#gold-node-glow)"
                  className="animate-pulse"
                />

                {/* Node Box */}
                <rect
                  width="200"
                  height="84"
                  rx="16"
                  className={`${theme.bg} transition-all duration-200`}
                  strokeWidth={isSelected ? 3 : 2}
                  stroke={isSelected ? "#C6A96B" : undefined}
                />

                {/* Node Header */}
                <text
                  x="14"
                  y="26"
                  className="font-mono text-[11px] font-bold uppercase tracking-wider fill-navy/70"
                >
                  {node.id}
                </text>

                {/* Category Badge */}
                <g transform="translate(130, 12)">
                  <rect
                    width="56"
                    height="18"
                    rx="9"
                    fill={theme.accent}
                    opacity="0.9"
                  />
                  <text
                    x="28"
                    y="13"
                    textAnchor="middle"
                    fill="#FFFFFF"
                    className="font-display text-[9px] font-bold uppercase tracking-wider"
                  >
                    {node.category}
                  </text>
                </g>

                {/* Tool Name */}
                <text
                  x="14"
                  y="50"
                  className="font-mono text-[12px] font-bold fill-navy"
                  style={{ wordBreak: "break-all" }}
                >
                  {node.task.tool.length > 22
                    ? `${node.task.tool.slice(0, 20)}…`
                    : node.task.tool}
                </text>

                {/* Source Description */}
                <text
                  x="14"
                  y="68"
                  className="text-[10px] font-medium fill-navy/55"
                >
                  {node.task.source.length > 26
                    ? `${node.task.source.slice(0, 24)}…`
                    : node.task.source}
                </text>

                {/* Parallel Pill */}
                {isParallel && (
                  <g transform="translate(155, 60)">
                    <text
                      x="0"
                      y="10"
                      textAnchor="middle"
                      fill="#9E8047"
                      className="font-display text-[9px] font-extrabold uppercase"
                    >
                      ∥ PARALLEL
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute bottom-3 left-3 right-3 z-10 flex items-center justify-between rounded-2xl border border-navy/15 bg-white/95 p-4 shadow-xl backdrop-blur-md animate-in slide-in-from-bottom duration-200">
            <div className="flex items-center gap-3 min-w-0">
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl font-mono text-xs font-bold text-white shadow-sm ${
                  selectedNode.category === "trigger"
                    ? "bg-blue-600"
                    : selectedNode.category === "output"
                    ? "bg-purple-600"
                    : "bg-emerald-600"
                }`}
              >
                {selectedNode.id}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm font-bold text-navy truncate">
                    {selectedNode.task.tool}
                  </span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase ${
                      selectedNode.category === "trigger"
                        ? "bg-blue-100 text-blue-800"
                        : selectedNode.category === "output"
                        ? "bg-purple-100 text-purple-800"
                        : "bg-emerald-100 text-emerald-800"
                    }`}
                  >
                    {selectedNode.category}
                  </span>
                  {selectedNode.task.parallel && (
                    <span className="rounded-full bg-gold/20 px-2 py-0.5 text-[10px] font-bold text-gold-deep">
                      Parallel
                    </span>
                  )}
                </div>
                <p className="text-xs text-navy/60 mt-0.5 truncate">
                  Source: {selectedNode.task.source} &bull; Dependencies:{" "}
                  {selectedNode.task.deps?.join(", ") || "None (Root Trigger)"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => setSelectedNodeId(null)}
                className="rounded-xl border border-navy/15 px-3 py-1.5 text-xs font-semibold text-navy/70 hover:bg-navy/5"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
