<template>
        <div id="background">
            <Marquee-text :duration="60">
                <p># flash_decision</p>
            </Marquee-text>
        </div>
</template>


<script>
    export default {
        name: "Backgroud",
        props: {}
    }
</script>


<style scoped>
    #background {
        font-size: 288px;
        color: #000000;
        opacity: 0.05;
        z-index: -1;
        position: absolute;
        display: block;
        width: 100%;
        top: 0%;
        text-align: center;
    }
</style>