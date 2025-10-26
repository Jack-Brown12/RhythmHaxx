<script lang="ts">
	import { importLibrary } from '@googlemaps/js-api-loader';
	import { onMount } from 'svelte';

	import Sidebar from '../Sidebar.svelte';
	import { getTotalDistanceKm } from '$lib/mapUtils';

	let map: google.maps.Map;

	let mapEl: HTMLDivElement;

	let endMarker: google.maps.marker.AdvancedMarkerElement | null = null;

	let length = $state(0);

	const { mapifiedPath } = $props();

	onMount(async () => {
		if (!window || !mapEl) return;
		const { Map } = await importLibrary('maps');
		await importLibrary('geometry');
		const { AdvancedMarkerElement } = await importLibrary('marker');

		map = new Map(mapEl, {
			center: { lat: 43.4772382, lng: -80.5520715 },
			mapId: 'main',
			zoom: 13,
			disableDefaultUI: true
		});
		if (!mapifiedPath) return;

		// @ts-expect-error
		const path = mapifiedPath!.map(([lat, lng]) => ({ lat, lng }));

		length = getTotalDistanceKm(path);

		new google.maps.Polyline({
			path,
			map,
			geodesic: true,
			strokeColor: 'black',
			strokeOpacity: 1,
			strokeWeight: 3
		});

		const startPos = path[0];
		const endPos = path[path.length - 1];

		new AdvancedMarkerElement({
			position: startPos,
			map,
			content: Object.assign(document.createElement('div'), {
				style: `
      					width: 12px;
      					height: 12px;
      					background-color: green;
      					border-radius: 50%;
      					border: 2px solid white;
    				`
			})
		});

		if (endMarker) {
			endMarker.map = null;
		}

		endMarker = new AdvancedMarkerElement({
			position: endPos,
			map,
			content: Object.assign(document.createElement('div'), {
				style: `
						width: 12px;
						height: 12px;
						background-color: red;
						border-radius: 50%;
						border: 2px solid white;
					`
			})
		});

		const center = path.reduce(
			// @ts-expect-error
			(acc, cur) => ({
				lat: acc.lat + cur.lat,
				lng: acc.lng + cur.lng
			}),
			{ lat: 0, lng: 0 }
		);

		center.lat /= path.length;
		center.lng /= path.length;

		map.panTo(center);
	});
</script>

<div class="flex flex-row">
	<Sidebar
		onButtonClick={() => {}}
		description="Here is your mapified path! If its not what you expected, feel free to go back and adjust your address or rotation."
		buttonText=""
		buttonEnabled={false}
	/>
	<div class="relative h-screen w-full">
		<div bind:this={mapEl} class="h-full w-full"></div>
		<div
			class="absolute top-3 right-3 rounded-xl border border-gray-300 bg-white/80 px-4 py-2 text-sm font-semibold text-gray-800 shadow-lg backdrop-blur-md"
		>
			Estimated Distance: {length.toFixed(2)} km
		</div>
	</div>
</div>
