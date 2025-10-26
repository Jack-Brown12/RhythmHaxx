<script lang="ts">
    import Stage1 from '$lib/components/Stages/Stage1.svelte';
    import Stage2 from '$lib/components/Stages/Stage2.svelte';
    import Stage3 from '$lib/components/Stages/Stage3.svelte';

    // REMOVE THIS IMPORT:
    // import { PUBLIC_MAPS_API_KEY } from '$env/static/public';

    import { toast } from '@zerodevx/svelte-toast';
    import { onMount } from 'svelte';
    import { setOptions } from '@googlemaps/js-api-loader';

    // Define a variable to hold the API key
    let mapsApiKey: string | undefined;

    let stage = 0;
    let points: [number, number][] | null = null;
    let mapifiedPath: [number, number][];

    onMount(async () => {
        try {
            // 1. Fetch the config from the Flask backend
            const response = await fetch('/api/config');
            const config = await response.json();

            if (response.ok && config.mapsApiKey) {
                mapsApiKey = config.mapsApiKey;

                // 2. Use the fetched key to set the loader options
                setOptions({ key: mapsApiKey });
            } else {
                // Handle API key not found or server error
                throw new Error(config.error || 'Failed to load configuration.');
            }
        } catch (error) {
            console.error('Configuration load error:', error);
            // Display an error toast if the config fails to load
            toast.push(`Configuration Error: ${error.message}`, {
                theme: {
                    '--toastBackground': 'red',
                    '--toastColor': 'white',
                    '--toastBarBackground': 'white'
                }
            });
        }
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

          fetch(`/api/mapify`, {
             method: 'POST',
             headers: {
                'Content-Type': 'application/json'
             },
             body: JSON.stringify({ points: latLngArray })
          })
             .then((response) => response.json())
             .then((data) => {
                mapifiedPath = data.points;
                stage += 1;
             })
             .catch((error) => {
                toast.push(`Error: ${error}`, {
                   theme: {
                      '--toastBackground': 'red',
                      '--toastColor': 'white',
                      '--toastBarBackground': 'white'
                   }
                });
             });
       }
    };
</script>

{#if mapsApiKey}
    {#if stage === 0}
        <Stage1 {nextStage} />
    {:else if stage === 1}
        <Stage2 {points} {nextStage} />
    {:else if stage === 2}
        <Stage3 {mapifiedPath} />
    {/if}
{:else}
    <p>Loading configuration...</p>
{/if}