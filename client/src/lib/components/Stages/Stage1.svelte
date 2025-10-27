<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import Sidebar from "../Sidebar.svelte";
    import { setupHiDPI } from "$lib/canvasUtils";

    const { nextStage } = $props();

    let canvasElement: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null = null;

    const pointEveryDistance = 1;
    let drawing = false;
    let locked = $state(false);

    let points: [number, number][] = [];
    let queue: [number, number][] = [];
    let rafId = 0;

    const schedule = () => {
        if (!rafId) rafId = requestAnimationFrame(drawPaths);
    };

    const drawPaths = () => {
        rafId = 0;
        if (!ctx || queue.length === 0) return;

        ctx.beginPath();

        let [px, py] = points.at(-1) ?? queue.shift()!;
        if (points.length === 0) points.push([px, py]);
        ctx.moveTo(px, py);

        while (queue.length) {
            const [x, y] = queue.shift()!;
            if (Math.hypot(x - px, y - py) >= pointEveryDistance) {
                ctx.lineTo(x, y);
                points.push([x, y]);
                px = x;
                py = y;
            }
        }

        ctx.stroke();
    };

    const onPointerDown = (e: PointerEvent) => {
        if (locked) {
            queue = [];
            points = [];

            ctx?.clearRect(0, 0, canvasElement.width, canvasElement.height);
            locked = false;
        }
        drawing = true;

        const x = e.clientX - canvasElement.offsetLeft;
        const y = e.clientY - canvasElement.offsetTop;

        queue.push([x, y]);

        schedule();
    };

    const onPointerMove = (e: PointerEvent) => {
        if (!drawing || locked) return;
        const x = e.clientX - canvasElement.offsetLeft;
        const y = e.clientY - canvasElement.offsetTop;

        queue.push([x, y]);
        schedule();
    };

    const onPointerUp = (e: PointerEvent) => {
        if (points.length >= 10) locked = true;
    };

    onMount(() => {
        ctx = canvasElement.getContext("2d");
        if (typeof window === "undefined" || !ctx) return;

        setupHiDPI(ctx, canvasElement);

        ctx.strokeStyle = "black";
        ctx.lineWidth = 2;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";

        window.addEventListener("pointerup", onPointerUp);
        window.addEventListener("resize", () => setupHiDPI(ctx!, canvasElement));
    });

    onDestroy(() => {
        if (typeof window === "undefined") return;
        window.removeEventListener("pointerup", onPointerUp);
        window.removeEventListener("resize", () => setupHiDPI(ctx!, canvasElement));
        if (rafId) cancelAnimationFrame(rafId);
    });
</script>

<div class="flex flex-row">
    <Sidebar
        onButtonClick={() => nextStage(points)}
        description="To get started, click and drag a continuous route on the white canvas. Don't release until you're
		done! If you mess up, just click again to redraw on a fresh canvas."
        buttonText="Insert onto the globe!"
        buttonEnabled={locked}
    />

    <canvas
        class="h-screen w-full"
        bind:this={canvasElement}
        onpointerdown={onPointerDown}
        onpointermove={onPointerMove}
        onpointerleave={onPointerUp}
    ></canvas>
</div>
