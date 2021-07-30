<template>
    <div id="app">

        <section class="title">
            <div id="layout_title">
                <h1 class="text_default title">{{ title }}</h1>
            </div>

            <div id="layout_separator_01">
                <div class="separator"></div>
            </div>

            <div id="layout_subtitle">
                <p class="text_default subtitle">{{page_name}}</p>
            </div>

            <div id="layout_separator_02">
                <div class="separator"></div>
            </div>
        </section>

    </div>
</template>

<script>
    export default {
        name: 'Title',
        props: {
            title: String,
            page_name: {
                type: String,
                required: true,
                default: ''
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    .title {
        text-align: center;
        font-size: 48px;
    }

    #layout_title {
        position: relative;
        width: 100%;
        height: 110px;
        line-height: 110px;
        display: flex;
        justify-content: center;
        flex-direction: column;
    }

    #layout_separator_01 {
        position: relative;
        width: 100%;
    }

    .separator {
        border-bottom: 1px solid #464646;
    }

    #layout_subtitle {
        position: relative;
        width: 100%;
        line-height: 50px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #464646;
        margin: auto;
    }

    #layout_separator_02 {
        position: relative;
        width: 100%;
    }

</style>
