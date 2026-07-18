/** Color estable por materia (mismo tono para todas sus cátedras). */
export function colorMateria(materiaId: string): string {
  let h = 0;
  for (let i = 0; i < materiaId.length; i++) {
    h = (h * 31 + materiaId.charCodeAt(i)) % 360;
  }
  return `hsl(${h} 70% 62%)`;
}
