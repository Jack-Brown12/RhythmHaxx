<script lang="ts">
	import { importLibrary } from '@googlemaps/js-api-loader';

	import Sidebar from '../Sidebar.svelte';
	import { onMount } from 'svelte';
	import { buildLatLngPathFromPixels, getTotalDistanceKm, rotatePoints } from '$lib/mapUtils';

	let map: google.maps.Map;
	let ac: google.maps.places.Autocomplete;

	let mapEl: HTMLDivElement;
	let inputEl: HTMLInputElement;

	let drawOnMap: () => void;
	let pixelsPerKm = 1000 / 20;
	let rotation = 0;
	let loc: google.maps.LatLng | undefined;

	let polyline: google.maps.Polyline | null = null;
	let endMarker: google.maps.marker.AdvancedMarkerElement | null = null;

	let addressSelected = $state(false);
	let length = $state(0);
	let buttonText = $state('Mapify!');

	const { points, nextStage } = $props();

	onMount(async () => {
		if (!window || !mapEl) return;
		const { Map } = await importLibrary('maps');
		const places = await importLibrary('places');
		await importLibrary('geometry');
		const { AdvancedMarkerElement } = await importLibrary('marker');

		map = new Map(mapEl, {
			center: { lat: 43.4772382, lng: -80.5520715 },
			mapId: 'main',
			zoom: 13,
			disableDefaultUI: true,
			gestureHandling: 'none',
			zoomControl: true,
			keyboardShortcuts: false,
			disableDoubleClickZoom: true
		});

		drawOnMap = () => {
			if (!loc || !points || points.length === 0) return;

			const start = { lat: loc.lat(), lng: loc.lng() };

			const path = buildLatLngPathFromPixels(rotatePoints(points, rotation), start, pixelsPerKm);

			length = getTotalDistanceKm(path);

			if (polyline) {
				polyline.setMap(null);
			}

			polyline = new google.maps.Polyline({
				path,
				map,
				geodesic: true,
				strokeColor: 'black',
				strokeOpacity: 1,
				strokeWeight: 3
			});

			const startPos = path[0];
			const endPos = path[path.length - 1];

			const style = `
      					width: 12px;
      					height: 12px;
      					background-color: green;
      					border-radius: 50%;
      					border: 2px solid white;
    				`;

			new AdvancedMarkerElement({
				position: startPos,
				map,
				content: Object.assign(document.createElement('div'), {
					style: style
				})
			});

			if (endMarker) {
				endMarker.map = null;
			}

			endMarker = new AdvancedMarkerElement({
				position: endPos,
				map,
				content: Object.assign(document.createElement('div'), {
					style: style
				})
			});

			const center = path.reduce(
				(acc, cur) => ({
					lat: acc.lat + cur.lat,
					lng: acc.lng + cur.lng
				}),
				{ lat: 0, lng: 0 }
			);

			center.lat /= path.length;
			center.lng /= path.length;

			map.panTo(center);
		};

		ac = new places.Autocomplete(inputEl, {
			fields: ['place_id', 'geometry', 'name', 'formatted_address'],
			types: ['geocode']
		});

		ac.addListener('place_changed', () => {
			const place = ac.getPlace();
			loc = place?.geometry?.location;
			if (!loc) return;

			addressSelected = true;

			drawOnMap();
		});
	});

	const submitHandler = (e: Event) => {
		e.preventDefault();
	};
</script>

<div class="flex flex-row">
	<Sidebar
		onButtonClick={() => {
			buttonText = 'Mapping...';
			nextStage(polyline);
		}}
		description="Time to place your masterpiece on the globe! Start by entering the address you want to start from. Afterwards, use the two sliders to adjust the size and rotation of your drawing."
		{buttonText}
		buttonEnabled={addressSelected}
	/>
	<div class="relative h-screen w-full">
		<form onsubmit={submitHandler}>
			<div class="absolute top-4 left-1/2 z-10 w-96 -translate-x-1/2">
				<input
					bind:this={inputEl}
					type="text"
					placeholder="Enter starting location..."
					class="w-full rounded-lg border border-gray-300 bg-white/90 px-4 py-2 shadow-lg outline-none focus:ring-2 focus:ring-blue-500"
				/>
			</div>
		</form>

		{#if !addressSelected}
			<div
				class="absolute top-1/2 left-1/2 z-10 -translate-x-1/2 -translate-y-1/2 rounded-2xl border border-gray-300 bg-white/80 px-6 py-4 shadow-lg backdrop-blur-md"
			>
				Please enter a starting location to see your route on the map.
			</div>
		{:else}
			<div
				class="absolute bottom-6 left-1/2 z-10 flex -translate-x-1/2 flex-col items-center space-y-3 rounded-2xl border border-gray-300 bg-white/80 px-4 py-3 shadow-lg backdrop-blur-md"
			>
				<div class="flex w-full flex-col items-center">
					<label for="rotation-slider" class="mb-1 text-xs font-medium text-gray-700">
						Rotation (°)
					</label>
					<input
						id="rotation-slider"
						type="range"
						min="-180"
						max="180"
						step="1"
						value="0"
						class="h-2 w-64 cursor-pointer appearance-none rounded-lg bg-gray-200 accent-black"
						oninput={(e) => {
							const val = +(e.target as HTMLInputElement).value;
							rotation = val;
							drawOnMap();
						}}
					/>
				</div>

				<div class="flex w-full flex-col items-center">
					<label for="scale-slider" class="mb-1 text-xs font-medium text-gray-700">
						Scale (pixels/km)
					</label>
					<input
						id="scale-slider"
						type="range"
						min="1"
						max="40"
						step="0.5"
						value="20"
						class="h-2 w-64 cursor-pointer appearance-none rounded-lg bg-gray-200 accent-black"
						oninput={(e) => {
							const val = +(e.target as HTMLInputElement).value;
							pixelsPerKm = 1000 / val;
							drawOnMap();
						}}
					/>
				</div>
			</div>
		{/if}

		<div bind:this={mapEl} class="h-full w-full"></div>
	</div>
</div>

{#if addressSelected}
	<div
		class="absolute top-3 right-3 rounded-xl border border-gray-300 bg-white/80 px-4 py-2 text-sm font-semibold text-gray-800 shadow-lg backdrop-blur-md"
	>
		Estimated Distance: {length.toFixed(2)} km
	</div>
{/if}
