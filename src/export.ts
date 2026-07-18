import type { Catedra } from "./types";
import { nombreDe } from "./data";
import { colorMateria } from "./color";

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"];

const aMin = (hhmm: string): number => {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
};

/** Rango horario (en minutos, redondeado a la hora) que cubren las clases. */
export function rangoHorario(catedras: Catedra[]): { min: number; max: number } | null {
  const clases = catedras.flatMap((c) => c.clases);
  if (clases.length === 0) return null;
  const min = Math.floor(Math.min(...clases.map((c) => aMin(c.inicio))) / 60) * 60;
  const max = Math.ceil(Math.max(...clases.map((c) => aMin(c.fin))) / 60) * 60;
  return { min, max };
}

// Dimensiones del dibujo (px lógicos).
const PX_MIN = 1.15;
const AXIS = 52;
const HEADER = 40;
const DAY_W = 158;
const PAD = 16;

function wrapText(
  ctx: CanvasRenderingContext2D,
  texto: string,
  x: number,
  y: number,
  maxW: number,
  lh: number,
): number {
  const palabras = texto.split(" ");
  let linea = "";
  for (const p of palabras) {
    const prueba = linea ? `${linea} ${p}` : p;
    if (ctx.measureText(prueba).width > maxW && linea) {
      ctx.fillText(linea, x, y);
      y += lh;
      linea = p;
    } else {
      linea = prueba;
    }
  }
  if (linea) {
    ctx.fillText(linea, x, y);
    y += lh;
  }
  return y;
}

/** Descarga la grilla del horario elegido como PNG. */
export function descargarPNG(catedras: Catedra[]): void {
  const rango = rangoHorario(catedras);
  if (!rango) return;
  const { min, max } = rango;

  const bodyH = (max - min) * PX_MIN;
  const W = PAD * 2 + AXIS + DAY_W * 5;
  const H = PAD * 2 + HEADER + bodyH;

  const escala = 2; // nitidez en pantallas retina
  const canvas = document.createElement("canvas");
  canvas.width = W * escala;
  canvas.height = H * escala;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.scale(escala, escala);

  // Fondo blanco (imagen legible en cualquier fondo).
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, W, H);

  const ox = PAD + AXIS;
  const oy = PAD + HEADER;

  // Encabezados de día.
  ctx.fillStyle = "#1c1c22";
  ctx.font = "600 13px system-ui, sans-serif";
  ctx.textAlign = "center";
  DIAS.forEach((d, i) => ctx.fillText(d, ox + DAY_W * i + DAY_W / 2, PAD + 24));

  // Líneas y etiquetas de hora.
  ctx.font = "11px system-ui, sans-serif";
  for (let h = min; h <= max; h += 60) {
    const y = oy + (h - min) * PX_MIN;
    ctx.strokeStyle = "#e6e6ee";
    ctx.beginPath();
    ctx.moveTo(ox, y);
    ctx.lineTo(ox + DAY_W * 5, y);
    ctx.stroke();
    ctx.fillStyle = "#6b6b78";
    ctx.textAlign = "right";
    ctx.fillText(`${String(Math.floor(h / 60)).padStart(2, "0")}:00`, ox - 6, y + 4);
  }
  // Divisiones verticales de día.
  ctx.strokeStyle = "#e6e6ee";
  for (let i = 0; i <= 5; i++) {
    const x = ox + DAY_W * i;
    ctx.beginPath();
    ctx.moveTo(x, oy);
    ctx.lineTo(x, oy + bodyH);
    ctx.stroke();
  }

  // Bloques de clase.
  for (const c of catedras) {
    for (const cl of c.clases) {
      const x = ox + DAY_W * (cl.dia - 1) + 3;
      const y = oy + (aMin(cl.inicio) - min) * PX_MIN + 1;
      const w = DAY_W - 6;
      const alto = (aMin(cl.fin) - aMin(cl.inicio)) * PX_MIN - 2;

      ctx.fillStyle = colorMateria(c.materiaId);
      ctx.beginPath();
      ctx.roundRect(x, y, w, alto, 6);
      ctx.fill();

      // Texto recortado al bloque para que no se desborde.
      ctx.save();
      ctx.beginPath();
      ctx.roundRect(x, y, w, alto, 6);
      ctx.clip();

      ctx.textAlign = "left";
      ctx.fillStyle = "#1c1c22";
      ctx.font = "600 11px system-ui, sans-serif";
      let ty = y + 14;
      ty = wrapText(ctx, nombreDe(c.materiaId), x + 6, ty, w - 12, 12);
      ctx.font = "10px system-ui, sans-serif";
      if (c.docente) {
        ctx.fillText(c.docente, x + 6, ty);
        ty += 12;
      }
      ctx.fillStyle = "#3a3a44";
      ctx.fillText(`${cl.inicio}–${cl.fin}`, x + 6, ty);
      ty += 12;
      if (cl.virtualidad) {
        ctx.font = "italic 9px system-ui, sans-serif";
        wrapText(ctx, `(${cl.virtualidad})`, x + 6, ty, w - 12, 10);
      }
      ctx.restore();
    }
  }

  canvas.toBlob((blob) => {
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "mi-horario.png";
    a.click();
    URL.revokeObjectURL(url);
  });
}
