<template>
    <!-- Chart Candels -->
    <div id="chart-candles" v-if="!isLoading">
        <Plotly style="height: 100%"
        :data="iterationChart['data']" 
        :layout="layout" 
        :responsive="true"
        :displayModeBar="false"
        :displaylogo="false"/>
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
                    autosize: true,
                    margin: {
                        r: 0,
                        t: 0,
                        b: 0,
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
                        x: 1,
                        y: 0.05,
                        xref: "paper",
                        yref: "paper",
                        axref: "paper",
                        text: "Position<br>autoclosing",
                        font: {color: "#333333", size: 10},
                        showarrow: true,
                        arrowhead: 0,
                        arrowsize: 1,
                        arrowwidth: 1.25,
                        arrowcolor: "#888888",
                        xanchor: "right",
                        ax: -20,
                        ay: 0
                        },
                        // Slippage zone hint
                        {
                        x: 0.15,
                        y: 0, // Will be set during formating
                        xref: "paper",
                        yref: "y",
                        text: "Slippage<br>zone",
                        font: {color: "#333333", size: 10},
                        showarrow: false,
                        xanchor: "right",
                        opacity: 0.5
                        }
                    ],
                    shapes: [
                        // Background
                        {
                        type: "rect",
                        xref: "paper",
                        yref: "paper",
                        x0: 0, // Will be set during formating
                        y0: 0,
                        x1: 1,
                        y1: 1,
                        fillcolor: "#d3d3d3",
                        opacity: 0.25,
                        line: {width: 0},
                        layer: "below"
                        },
                        // Last price line vertical
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
                        line: {width: 2},
                        layer: "above"
                        },
                        // Last price line horizontal
                        {
                        type: "line",
                        xref: "x",
                        yref: "y",
                        x0: 0, // Will be set during formating
                        y0: 0, // Will be set during formating
                        x1: 0, // Will be set during formating
                        y1: 0, // Will be set during formating
                        fillcolor: "#000000",
                        opacity: 0.25,
                        line: {width: 1},
                        layer: "above"
                        },
                        // Slippage zone
                        {
                        type: "rect",
                        xref: "paper",
                        yref: "y",
                        x0: 0,
                        y0: 0, // Will be set during formating
                        x1: 1,
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
                let totalbars = finalbar + fixingbar
                let priceLast = this.iterationChart["data"][0]["close"].at(-1)
                let priceMax = Math.max(...this.iterationChart["data"][0]["close"])
                let priceMin = Math.min(...this.iterationChart["data"][0]["close"])
                let slippage = parseFloat(this.currentSession["options"]["values"]["slippage"])

                // Update coordinates for text left
                this.layout.annotations[0].x = finalbar
                this.layout.annotations[0].y = priceLast
                this.layout.annotations[0].ax = fixingbar
                this.layout.annotations[0].ay = priceLast + ((priceMax - priceMin) / 10) * 1.5
                // Update coordinates for slippage zone hint
                this.layout.annotations[2].y = priceLast
                // Update coordinates for background (shift for 0.5bar back to the middle of the candle)
                this.layout.shapes[0].x0 = parseFloat((finalbar / totalbars - (0.5 / totalbars)).toFixed(2))
                // Update coordinates for border left
                this.layout.shapes[1].x0 = finalbar
                this.layout.shapes[1].x1 = finalbar
                // Update coordinates for price line
                this.layout.shapes[2].x0 = 0.5
                this.layout.shapes[2].x1 = totalbars
                this.layout.shapes[2].y0 = priceLast
                this.layout.shapes[2].y1 = priceLast
                // Update coordinates for slippage zone
                this.layout.shapes[3].y0 = priceLast * (1 + slippage)
                this.layout.shapes[3].y1 = priceLast * (1 - slippage)
            }
        }
    }

</script>

<style scoped>

    #chart-candles {
        border: 1px;
        border-color: #d3d3d3;
        border-style: solid;
        height: calc(100vh - 230px - 38px - 15px - 25px - 5px - 35px);
    }

</style>
