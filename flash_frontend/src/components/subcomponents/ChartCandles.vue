<template>
    <!-- Chart Candels -->
    <div id="chart-candels" v-if="!isLoading">
        <Plotly 
        :data="iterationChart['data']" 
        :layout="layout" 
        :displayModeBar="false"
        :displaylogo="false"/>
        <!-- :responsive="true" -->
    </div>
</template>

<script>
    import { mapState } from "vuex"
    import { Plotly } from "vue-plotly"

    export default {
        name: "ChartCandels",
        components: {
            Plotly
        },
        props: {
            iterationChart: Object
        },
        data() {
            return {
                // Chart layout properties
                layout: {
                    title: {visible: false},
                    showlegend: false,
                    dragmode: false,
                    height: (window.innerHeight > 700) ? window.innerHeight * 0.54 : window.innerHeight * 0.48,
                    autosize: true,
                    margin: {
                        r: 0,
                        t: 10,
                        b: 10,
                        l: 0
                    },
                    xaxis: {
                        autorange: true,
                        rangeslider: {visible: false},
                        title: {visible: false},
                        showticklabels: false,
                        },
                    annotations: [
                        // Text left
                        {
                        x: 0, // Will be set during formating
                        y: 0, // Will be set during formating
                        xref: "x",
                        yref: "y",
                        ayref: "y",
                        text: "Your<br>decision?",
                        font: {color: "#333333", size: 10},
                        showarrow: true,
                        arrowhead: 0,
                        arrowsize: 1,
                        arrowwidth: 1.25,
                        arrowcolor: "#888888",
                        xanchor: "left",
                        ax: 0, // Will be set during formating
                        ay: 0 // Will be set during formating
                        },
                        // Text right
                        {
                        x: 0, // Will be set during formating
                        y: 0.05,
                        xref: "x",
                        yref: "paper",
                        text: "Position<br>autoclosing",
                        font: {color: "#333333", size: 10},
                        showarrow: true,
                        arrowhead: 0,
                        arrowsize: 1,
                        arrowwidth: 1.25,
                        arrowcolor: "#888888",
                        xanchor: "right",
                        ax: 0, // Will be set during formating
                        ay: 0
                        }
                    ],
                    shapes: [
                        // Background
                        {
                        type: "rect",
                        xref: "x",
                        yref: "paper",
                        x0: 0, // Will be set during formating
                        y0: 0,
                        x1: 0, // Will be set during formating
                        y1: 1,
                        fillcolor: "#d3d3d3",
                        opacity: 0.2,
                        line: {width: 0},
                        layer: "below"
                        },
                        // Border left
                        {
                        type: "line",
                        xref: "x",
                        yref: "paper",
                        x0: 0, // Will be set during formating
                        y0: 0,
                        x1: 0, // Will be set during formating
                        y1: 1,
                        fillcolor: "#d3d3d3",
                        opacity: 0.25,
                        line: {width: 1},
                        layer: "above"
                        },
                        // Border right
                        {
                        type: "line",
                        xref: "x",
                        yref: "paper",
                        x0: 0, // Will be set during formating
                        y0: 0,
                        x1: 0, // Will be set during formating
                        y1: 1,
                        fillcolor: "#d3d3d3",
                        opacity: 0.25,
                        line: {width: 1},
                        layer: "above"
                        },
                        // Last price line
                        {
                        type: "line",
                        xref: "x",
                        yref: "y",
                        x0: 0, // Will be set during formating
                        y0: 0, // Will be set during formating
                        x1: 0, // Will be set during formating
                        y1: 0, // Will be set during formating
                        fillcolor: "#d3d3d3",
                        opacity: 0.25,
                        line: {width: 1},
                        layer: "above"
                        },
                        // Slippage zone
                        {
                        type: "rect",
                        xref: "x",
                        yref: "y",
                        x0: 0, // Will be set during formating
                        y0: 0, // Will be set during formating
                        x1: 0, // Will be set during formating
                        y1: 0, // Will be set during formating
                        fillcolor: "red",
                        opacity: 0.05,
                        line: {width: 0}
                        }
                        ]
                }
                }
        },
        computed: {
            ...mapState(["user", "currentSession", "isLoading"])
        },
        beforeMount() {
            // Change chart layout
            this.formatChart()
        },
        methods: {
            formatChart() {
                // Format chart - add extra space to the graph
                let finalbar = parseInt(this.currentSession["options"]["values"]["barsnumber"])
                let fixingbar = parseInt(this.currentSession["options"]["values"]["fixingbar"])
                let priceLast = this.iterationChart["data"][0]["close"].at(-1)
                let priceMax = Math.max(...this.iterationChart["data"][0]["close"])
                let priceMin = Math.min(...this.iterationChart["data"][0]["close"])
                let slippage = parseFloat(this.currentSession["options"]["values"]["slippage"])

                // Update coordinates for text left
                this.layout.annotations[0].x = finalbar
                this.layout.annotations[0].y = priceLast
                this.layout.annotations[0].ax = fixingbar
                this.layout.annotations[0].ay = priceLast + ((priceMax - priceMin) / 10) * 1.5
                // Update coordinates for text right
                this.layout.annotations[1].x = finalbar + fixingbar
                this.layout.annotations[1].ax = fixingbar * -1
                // Update coordinates for background
                this.layout.shapes[0].x0 = finalbar
                this.layout.shapes[0].x1 = finalbar + fixingbar
                // Update coordinates for border left
                this.layout.shapes[1].x0 = finalbar
                this.layout.shapes[1].x1 = finalbar
                // Update coordinates for border right
                this.layout.shapes[2].x0 = finalbar + fixingbar
                this.layout.shapes[2].x1 = finalbar + fixingbar
                // Update coordinates for price line
                this.layout.shapes[3].x0 = 0.5
                this.layout.shapes[3].x1 = finalbar + fixingbar
                this.layout.shapes[3].y0 = priceLast
                this.layout.shapes[3].y1 = priceLast
                // Update coordinates for background
                this.layout.shapes[4].x0 = 0.5
                this.layout.shapes[4].x1 = finalbar + fixingbar
                this.layout.shapes[4].y0 = priceLast * (1 + slippage)
                this.layout.shapes[4].y1 = priceLast * (1 - slippage)
            }
        }
    }

</script>

<style scoped>

</style>
