<script lang="ts">
    import Stage1 from "$lib/components/Stages/Stage1.svelte";
    import Stage2 from "$lib/components/Stages/Stage2.svelte";

    import { PUBLIC_API_BASE_ADDRESS, PUBLIC_MAPS_API_KEY } from "$env/static/public";

    import { toast } from "@zerodevx/svelte-toast";
    import { onMount } from "svelte";
    import { setOptions } from "@googlemaps/js-api-loader";
    import Stage3 from "$lib/components/Stages/Stage3.svelte";

    let stage = 0;

    let points: [number, number][] | null = null;
    let mapifiedPath: [number, number][];

    onMount(() => {
        setOptions({ key: PUBLIC_MAPS_API_KEY });
    });

    const nextStage = (stageOnePoints: [number, number][] | google.maps.Polyline) => {
        if (stage === 0) {
            // @ts-expect-error
            points = stageOnePoints;
            stage += 1;
        } else if (stage === 1) {
            const path = (stageOnePoints as google.maps.Polyline).getPath();
            const latLngArray: [number, number][] = [];
            path.forEach((latLng) => {
                latLngArray.push([latLng.lat(), latLng.lng()]);
            });

            fetch(`${PUBLIC_API_BASE_ADDRESS}/api/mapify`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                mode: "cors",
                body: JSON.stringify({ points: latLngArray }),
            })
                .then((response) => {
                    if (!response.ok) {
                        const code = response.status;
                        toast.push(`Did not get a 200 response! Returned code: ${code}`, {
                            theme: {
                                "--toastBackground": "red",
                                "--toastColor": "white",
                                "--toastBarBackground": "white",
                            },
                        });
                    }
                    response.json().then((data) => {
                        mapifiedPath = data.points;
                        stage += 1;
                    });
                })
                .catch((error) => {
                    const code = error?.code || "UNKNOWN";
                    const message =
                        (error && (error.message || String(error))) ?? "An error occurred";
                    toast.push(`Error (${code}): ${message}`, {
                        theme: {
                            "--toastBackground": "red",
                            "--toastColor": "white",
                            "--toastBarBackground": "white",
                        },
                    });
                    console.error("Error during mapification:", error);
                });
        }
    };
</script>

{#if stage === 0}
    <Stage1 {nextStage} />
{:else if stage === 1}
    <Stage2 {points} {nextStage} />
{:else if stage === 2}
    <Stage3 {mapifiedPath} />
{/if}
