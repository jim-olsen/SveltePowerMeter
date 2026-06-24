<script>
    import {weatherData} from "../../stores.svelte.js";

    export let size = 200;

    $: windDir = $weatherData?.windDir ? Number($weatherData.windDir) : null;
    $: windSpeed = $weatherData?.wind_average ? Number($weatherData.wind_average) : null;
    $: windGust = $weatherData?.windGust ? Number($weatherData.windGust) : null;

    $: r = size / 2;
    $: outerR = r * 0.92;
    $: tickOuter = r * 0.88;
    $: tickInner = r * 0.78;
    $: tickMinorInner = r * 0.82;
    $: labelR = r * 0.66;
    $: arrowLen = r * 0.52;
    $: arrowWidth = r * 0.10;

    const cardinals = [
        {angle: 0, label: 'N'},
        {angle: 45, label: 'NE'},
        {angle: 90, label: 'E'},
        {angle: 135, label: 'SE'},
        {angle: 180, label: 'S'},
        {angle: 225, label: 'SW'},
        {angle: 270, label: 'W'},
        {angle: 315, label: 'NW'},
    ];

    function tickEnd(angleDeg, radius) {
        const rad = (angleDeg - 90) * Math.PI / 180;
        return {x: Math.cos(rad) * radius, y: Math.sin(rad) * radius};
    }
</script>

<svg viewBox="{-r} {-r} {size} {size}" width="{size}" height="{size}" class="wind-rose">
    <!-- Outer ring -->
    <circle cx="0" cy="0" r="{outerR}" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="2"/>
    <circle cx="0" cy="0" r="{r * 0.38}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>

    <!-- Tick marks -->
    {#each Array(36) as _, i}
        {@const angle = i * 10}
        {@const isMajor = angle % 45 === 0}
        {@const inner = isMajor ? tickInner : tickMinorInner}
        {@const p1 = tickEnd(angle, tickOuter)}
        {@const p2 = tickEnd(angle, inner)}
        <line x1="{p1.x}" y1="{p1.y}" x2="{p2.x}" y2="{p2.y}"
              stroke="{isMajor ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.18)'}"
              stroke-width="{isMajor ? 2 : 1}"/>
    {/each}

    <!-- Cardinal labels -->
    {#each cardinals as c}
        {@const p = tickEnd(c.angle, labelR)}
        <text x="{p.x}" y="{p.y}" text-anchor="middle" dominant-baseline="central"
              class="cardinal" class:cardinal-main={c.label.length === 1}>
            {c.label}
        </text>
    {/each}

    <!-- Wind direction arrow -->
    {#if windDir != null}
        <g transform="rotate({windDir})">
            <!-- Arrow body -->
            <line x1="0" y1="{r * 0.30}" x2="0" y2="{-arrowLen}"
                  stroke="#FF5C5C" stroke-width="{Math.max(2, r * 0.04)}" stroke-linecap="round"/>
            <!-- Arrow head -->
            <polygon points="0,{-arrowLen - r * 0.06} {-arrowWidth},{-arrowLen + r * 0.10} {arrowWidth},{-arrowLen + r * 0.10}"
                     fill="#FF5C5C" opacity="0.95"/>
            <!-- Tail -->
            <circle cx="0" cy="{r * 0.30}" r="{r * 0.04}" fill="#FF5C5C" opacity="0.6"/>
        </g>
    {/if}

    <!-- Center info -->
    <text x="0" y="{-r * 0.06}" text-anchor="middle" class="wind-speed">
        {windSpeed != null ? windSpeed.toFixed(1) : '---'}
    </text>
    <text x="0" y="{r * 0.10}" text-anchor="middle" class="wind-unit">MPH</text>
    <text x="0" y="{r * 0.24}" text-anchor="middle" class="wind-dir">
        {windDir != null ? windDir.toFixed(0) + '°' : '--'}
    </text>
</svg>

<style>
    .wind-rose {
        display: block;
        max-width: 100%;
        max-height: 100%;
    }

    .cardinal {
        fill: #8892A6;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .cardinal-main {
        fill: #e6eaf2;
        font-size: 14px;
        font-weight: 700;
    }

    .wind-speed {
        fill: #fca503;
        font-size: 36px;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }

    @media (min-width: 1280px) and (min-height: 720px) {
        .wind-speed { font-size: 48px; }
    }

    .wind-unit {
        fill: #b0b9c8;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .wind-dir {
        fill: #8892A6;
        font-size: 11px;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
</style>



