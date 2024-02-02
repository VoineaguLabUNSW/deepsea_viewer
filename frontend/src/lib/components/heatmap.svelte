<script>
    import { scaleLinear, scaleSequential } from 'd3-scale'
    import { interpolateRgbBasis } from 'd3-interpolate'
    import { derived, writable } from 'svelte/store';
    import { afterUpdate, onMount} from 'svelte';
    import * as d3 from 'd3';

    export let data;

    export let subview = writable(undefined);
    const LEGEND_SIZE={x:300, y:20}
    const COLOR_STEPS = ["#440154","#440256","#450457","#450559","#46075a","#46085c","#460a5d","#460b5e","#470d60","#470e61","#471063","#471164","#471365","#481467","#481668","#481769","#48186a","#481a6c","#481b6d","#481c6e","#481d6f","#481f70","#482071","#482173","#482374","#482475","#482576","#482677","#482878","#482979","#472a7a","#472c7a","#472d7b","#472e7c","#472f7d","#46307e","#46327e","#46337f","#463480","#453581","#453781","#453882","#443983","#443a83","#443b84","#433d84","#433e85","#423f85","#424086","#424186","#414287","#414487","#404588","#404688","#3f4788","#3f4889","#3e4989","#3e4a89","#3e4c8a","#3d4d8a","#3d4e8a","#3c4f8a","#3c508b","#3b518b","#3b528b","#3a538b","#3a548c","#39558c","#39568c","#38588c","#38598c","#375a8c","#375b8d","#365c8d","#365d8d","#355e8d","#355f8d","#34608d","#34618d","#33628d","#33638d","#32648e","#32658e","#31668e","#31678e","#31688e","#30698e","#306a8e","#2f6b8e","#2f6c8e","#2e6d8e","#2e6e8e","#2e6f8e","#2d708e","#2d718e","#2c718e","#2c728e","#2c738e","#2b748e","#2b758e","#2a768e","#2a778e","#2a788e","#29798e","#297a8e","#297b8e","#287c8e","#287d8e","#277e8e","#277f8e","#27808e","#26818e","#26828e","#26828e","#25838e","#25848e","#25858e","#24868e","#24878e","#23888e","#23898e","#238a8d","#228b8d","#228c8d","#228d8d","#218e8d","#218f8d","#21908d","#21918c","#20928c","#20928c","#20938c","#1f948c","#1f958b","#1f968b","#1f978b","#1f988b","#1f998a","#1f9a8a","#1e9b8a","#1e9c89","#1e9d89","#1f9e89","#1f9f88","#1fa088","#1fa188","#1fa187","#1fa287","#20a386","#20a486","#21a585","#21a685","#22a785","#22a884","#23a983","#24aa83","#25ab82","#25ac82","#26ad81","#27ad81","#28ae80","#29af7f","#2ab07f","#2cb17e","#2db27d","#2eb37c","#2fb47c","#31b57b","#32b67a","#34b679","#35b779","#37b878","#38b977","#3aba76","#3bbb75","#3dbc74","#3fbc73","#40bd72","#42be71","#44bf70","#46c06f","#48c16e","#4ac16d","#4cc26c","#4ec36b","#50c46a","#52c569","#54c568","#56c667","#58c765","#5ac864","#5cc863","#5ec962","#60ca60","#63cb5f","#65cb5e","#67cc5c","#69cd5b","#6ccd5a","#6ece58","#70cf57","#73d056","#75d054","#77d153","#7ad151","#7cd250","#7fd34e","#81d34d","#84d44b","#86d549","#89d548","#8bd646","#8ed645","#90d743","#93d741","#95d840","#98d83e","#9bd93c","#9dd93b","#a0da39","#a2da37","#a5db36","#a8db34","#aadc32","#addc30","#b0dd2f","#b2dd2d","#b5de2b","#b8de29","#bade28","#bddf26","#c0df25","#c2df23","#c5e021","#c8e020","#cae11f","#cde11d","#d0e11c","#d2e21b","#d5e21a","#d8e219","#dae319","#dde318","#dfe318","#e2e418","#e5e419","#e7e419","#eae51a","#ece51b","#efe51c","#f1e51d","#f4e61e","#f6e620","#f8e621","#fbe723","#fde725"]
    const MUTATION_DISPLAY_ORDER = 'CGTA';
    const MUTATION_TYPES = [
        'AA', 'AG', 'AC', 'AT',
        'GA', 'GG', 'GC', 'GT',
        'CA', 'CG', 'CC', 'CT',
        'TA', 'TG', 'TC', 'TT'
    ];
    const CANVAS_RESOLUTION={x: 2000, y: 80};
    const CANVAS_HEIGHT=80;

    const color_scale = scaleSequential(interpolateRgbBasis(COLOR_STEPS)).domain([-0.5,0.5]);
    const margin = { top: 20, right: 25, bottom: 40, left: 25 };
    const type_to_order = MUTATION_TYPES.map(t => ({from: t[0], to: t[1], annot: `${t[0]}->${t[1]}`, y: MUTATION_DISPLAY_ORDER.indexOf(t[1])}));

    const plot_data = derived(data, ($data, set) => {
        console.log($data)
        if(!$data?.data) return;
        const cells = $data.data.types.map(t => type_to_order[t]);
        const headings = cells.filter((_, i) => !(i%3)).map(p => p.from)
        set({cells, headings, values: $data.data.values, timestamp: Date.now()})
    });

    let clientWidth, clientHeight, offsetWidth, offsetHeight;

	let width = 30000;
	let height = 300;

	let scrollMax = width;
	$: scrollMax = width - clientWidth;

    $: xScale = scaleLinear()
		.domain([0, $plot_data.headings.length])
		.range([margin.left, width-margin.right]);

	$: yScale = scaleLinear()
		.domain([0, MUTATION_DISPLAY_ORDER.length])
		.range([margin.top, height-margin.bottom]);

    $: legendScale = scaleLinear()
        .domain([-0.5, 0.5])
        .range([margin.left, LEGEND_SIZE.x-margin.right])

    let gx1, gx2, gy, glegend;
    $: d3.select(gy).call(d3.axisLeft(yScale).tickValues([...Array(MUTATION_DISPLAY_ORDER.length).keys()].map(i => i+0.5)).tickFormat(i => MUTATION_DISPLAY_ORDER[Math.floor(i)]));
    $: d3.select(gx2).call(d3.axisBottom(xScale).tickValues([...Array(2000/20).keys()].map(i => i*20)));
    $: d3.select(gx1).call(d3.axisTop(xScale).tickValues([...Array(2000).keys()]).tickFormat(d => $plot_data.headings[d]));
    $: d3.select(glegend).call(d3.axisBottom(legendScale).tickValues([-0.5, 0, 0.5]));

    let svg, canvas, container, canvas_timestamp;
    afterUpdate(() => {
        if ($plot_data.timestamp === canvas_timestamp) return;
        canvas_timestamp = $plot_data.timestamp
		const svg_url = new XMLSerializer().serializeToString(svg);
        const img = new Image();
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);;
        img.onload = function() {
            ctx.drawImage(this,
                -canvas.width * margin.left/width,
                -canvas.height * margin.top/height,
                canvas.width * (1+(margin.left+margin.right)/width),
                canvas.height * (1+(margin.top+margin.bottom)/height)
            );
        }
        img.src = 'data:image/svg+xml; charset=utf8, ' + encodeURIComponent(svg_url);
	});

    let leftPx, rightPx, leftCan, rightCan, scrollInit;

    function recenterScroll(smooth=false) {
        const leftPxUser = 0.5*(width) - clientWidth/2;
        container.scroll({left: leftPxUser, behavior: smooth ? "smooth" : undefined})
    }

    function smoothScroll(canvasEvent) {
        const rect = canvas.getBoundingClientRect();
        const scroll = (canvasEvent.clientX - rect.left) / (rect.right - rect.left);
        const leftPxUser = scroll * width - clientWidth/2;
        container.scroll({left: leftPxUser, behavior: "smooth"})
    }

    $: {
        // Recalculate base scroll when client width changes
        if(container && !isNaN(clientWidth) && !scrollInit) {;
            recenterScroll();
            scrollInit = true;
        }
    }
    $: {
        // Recalculate canvas scroll whenever base scroll changes
        if(!isNaN(leftPx)) {
            rightPx = leftPx + clientWidth;
            leftCan = leftPx / width * 100;
            rightCan = rightPx / width * 100;
        }
    }
</script>

 <div class="h-full w-full" bind:clientWidth bind:clientHeight bind:offsetWidth bind:offsetHeight role="none" on:dblclick={() => recenterScroll(true)}>
    <div class='w-full h-16'>
        <div class='float-right text-center'>
            <svg width={LEGEND_SIZE.x} height=50>
                <!-- legend -->
                <defs>
                    <linearGradient id="legend-gradient">
                        {#each COLOR_STEPS as c, i}
                            <stop offset="{i/(COLOR_STEPS.length-1)*100.0}%" stop-color={c} />
                        {/each}
                    </linearGradient>
                </defs>
                <g bind:this={glegend} transform="translate({0},{30})"/>
                <rect width="{LEGEND_SIZE.x-margin.left-margin.right}" height=10 y=20 x={margin.left} fill="url(#legend-gradient)"/>
                <text x="50%" y="10" dominant-baseline="middle" text-anchor="middle">Log-fold change</text>
            </svg>
        </div>
    </div>
    <div>
      <svg height={height} width={margin.left} class="absolute pointer-events-none z-10 bg-white">
            <!-- y axis -->
            <g transform="translate({margin.left},0)" bind:this={gy}/>
        </svg>
        <div bind:this={container} style="margin-right:{margin.right}px" class="overflow-x-scroll [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]" on:scroll={(e) => (leftPx=e.target.scrollLeft)}>
                <svg bind:this={svg} width={width} height={height}>

                    <!-- cells -->
                    {#if $plot_data}
                        {@const rect_w=(width-margin.left-margin.right)/$plot_data.headings.length}
                        {@const rect_h=(height-margin.top-margin.bottom)/MUTATION_DISPLAY_ORDER.length}
                        {#each $plot_data.cells as cell, i }
                            {@const cellX=Math.floor(i/3)}
                            <rect width={rect_w} height={rect_h} y={yScale(cell.y)} x={xScale(cellX)} opacity={(!$subview || Math.abs(cellX - 1000) <= $subview) ? 1 : 0.5} fill={color_scale($plot_data.values[i])}>
                                <title>{cell.annot} ({$plot_data.values[i]})</title>
                            </rect>
                        {/each}

                        <!-- x axis top -->
                        <g transform="translate({rect_w/2},{margin.top})" bind:this={gx1}/>

                        <!-- x axis bottom -->
                        <g transform="translate({rect_w/2},{height-margin.bottom})" bind:this={gx2}/>

                        <!-- center line -->
                        <line stroke="black" stroke-dasharray="10,10" stroke-width="4" x1={xScale(1000.5)} y1={yScale(0)} x2={xScale(1000.5)} y2={yScale(4)}></line>
                        <line stroke="white" stroke-dasharray="10,10" stroke-width="2" x1={xScale(1000.5)} y1={yScale(0)} x2={xScale(1000.5)} y2={yScale(4)}></line>
                    {/if}
                </svg>
        </div>
    </div>
</div>
<div class="relative border border-black border-1 opacity-75 hover:opacity-100 transition-opacity duration-50">
    <div style="left:{leftCan}%; right:{100-rightCan}%; height:{CANVAS_HEIGHT}px" class="absolute bg-white opacity-50 border border-black border-1 pointer-events-none"></div>
    <canvas on:mousedown={smoothScroll} bind:this={canvas} width={CANVAS_RESOLUTION.x} height={CANVAS_RESOLUTION.y} style="height:{CANVAS_HEIGHT}px" class="w-full"></canvas>
</div>
