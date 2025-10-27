export const buildLatLngPathFromPixels = (
    points: [number, number][],
    start: google.maps.LatLngLiteral,
    pixelsPerKm: number
): google.maps.LatLngLiteral[] => {
    if (!points || points.length === 0) return [];

    const path: google.maps.LatLngLiteral[] = [];
    let cur = start;
    path.push(cur);

    for (let i = 1; i < points.length; i++) {
        const [x0, y0] = points[i - 1];
        const [x1, y1] = points[i];

        const dx = x1 - x0;
        const dy = y1 - y0;

        const segPixels = Math.hypot(dx, dy);
        if (segPixels === 0) {
            path.push(cur);
            continue;
        }

        const km = segPixels / pixelsPerKm;
        const meters = km * 1000;

        const heading = ((Math.atan2(dx, -dy) * 180) / Math.PI + 360) % 360;

        const next = google.maps.geometry.spherical.computeOffset(cur, meters, heading);
        cur = { lat: next.lat(), lng: next.lng() };
        path.push(cur);
    }

    return path;
};

export const getTotalDistanceKm = (path: google.maps.LatLngLiteral[]): number => {
    if (!path || path.length < 2) return 0;

    const latLngs = path.map((p) => new google.maps.LatLng(p.lat, p.lng));

    const totalMeters = google.maps.geometry.spherical.computeLength(latLngs);

    return totalMeters / 1000;
};

export const rotatePoints = (points: [number, number][], angleDeg: number): [number, number][] => {
    if (!points || points.length === 0) return [];
    if (points.length === 1) return [points[0]];

    const [cx, cy] = points[0];
    const theta = (angleDeg * Math.PI) / 180;
    const cos = Math.cos(theta);
    const sin = Math.sin(theta);

    return points.map(([x, y], i) => {
        if (i === 0) return [x, y];
        const dx = x - cx;
        const dy = y - cy;

        const rx = dx * cos - dy * sin;
        const ry = dx * sin + dy * cos;

        return [cx + rx, cy + ry];
    });
};
