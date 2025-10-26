<script lang="ts">
	import Stage1 from '$lib/components/Stages/Stage1.svelte';
	import Stage2 from '$lib/components/Stages/Stage2.svelte';

	import { toast } from '@zerodevx/svelte-toast';
	import { onMount } from 'svelte';
	import { setOptions } from '@googlemaps/js-api-loader';
	import Stage3 from '$lib/components/Stages/Stage3.svelte';

	let stage = 0;

	let points: [number, number][] | null = null;
	let mapifiedPath: [number, number][];

	onMount(async () => {
        try {
            const response = await fetch('/api/config');
            if (!response.ok) {
                throw new Error('Failed to fetch config');
            }
            const config = await response.json();

            // Use the key fetched from the Flask backend
            setOptions({ key: config.mapsApiKey });

        } catch (error) {
            toast.push(`Error loading config: ${error}`, {
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

{#if stage === 0}
	<Stage1 {nextStage} />
{:else if stage === 1}
	<Stage2 {points} {nextStage} />
{:else if stage === 2}
	<Stage3 {mapifiedPath} />
{/if}
