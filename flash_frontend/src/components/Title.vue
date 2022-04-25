<template>
    <section id="title">
        <div id="layout-title" class="shadow">
            <div id="layout-title-left">
                <h1 id="title-letter">{{ title.charAt(0).toUpperCase() }}</h1>
            </div>
            <div id="layout-title-right">
                <h1 id="title">{{ title }}</h1>
            </div>
        </div>

        <div id="layout-subtitle">
            <h2 class="subtitle">{{ instruction }}</h2>
        </div>
    </section>
</template>

<script>
    export default {
        name: "Title",
        props: {},
        computed: {
            title() {
                return this.$route.meta.title
            },
            instruction() {
                return this.$route.meta.instruction
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    #layout-title {
        height: 64px;
        margin: 25px;
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        background-color: #FFFFFF;
        border-bottom: 0.5px solid #0B5A73;
    }

    #layout-title-left {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 64px;
        background: linear-gradient(to right, #271238, #113763, #0B5A73);
        color: #ffffff;
    }

    #layout-title-right {
        width: 339px;
    }

    #layout-subtitle {
        position: relative;
        max-width: 100%;
        margin: 0px 25px;
    }

    #title {
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        margin: 0px;
    }
    
    @media (max-width: 700px) {
        #title {
            font-size: 20px;
        }
    }

    #title-letter {
        font-size: 48px;
        font-weight: 900;
    }

    .subtitle {
        text-align: center;
        font-size: 16px;
        font-weight: 500;
    }

</style>
