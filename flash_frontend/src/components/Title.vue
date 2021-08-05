<template>
    <div id="app">

        <section class="title">
            <div id="layout_title">
                <div id="layout_title_left"><h1 id="title_letter">{{ title.charAt(0).toUpperCase() }}</h1></div>
                <div id="layout_title_right"><h1 id="title">{{ title }}</h1></div>
            </div>

            <div id="layout_subtitle">
                <p class="subtitle">{{ instruction }}</p>
            </div>
        </section>

    </div>
</template>

<script>
    export default {
        name: 'Title',
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

    #layout_title {
        height: 64px;
        margin: 25px;
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        background-color: #ffffff;
        border-bottom: 0.5px solid #0B5A73;
    }

    #layout_title_left {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 64px;
        background-color: #0B5A73;
        color: #ffffff;
    }

    #layout_title_right {
        width: 339px;
    }

    #layout_subtitle {
        position: relative;
        width: 100%;
    }

    #title {
        text-align: center;
        font-size: 24px;
        font-weight: 700;
    }

    #title_letter {
        font-size: 48px;
        font-weight: 900;
    }

    .subtitle {
        text-align: center;
        font-size: 14px;
        font-weight: 500;
    }

</style>
