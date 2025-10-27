export const setupHiDPI = (
    ctx: CanvasRenderingContext2D | null,
    canvasElement: HTMLCanvasElement
) => {
    if (!ctx || !canvasElement) return;
    const dpr = window.devicePixelRatio || 1;
    const rect = canvasElement.getBoundingClientRect();
    canvasElement.width = rect.width * dpr;
    canvasElement.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
};
