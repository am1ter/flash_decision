<template>
    <section id="title" :class="{shift_header: !isAuth}">
        <div id="layout-title" class="shadow">
            <div id="layout-title-left">
                <h1 id="title-letter">{{ title.charAt(0).toUpperCase() }}</h1>
            </div>
            <div id="layout-title-right">
                <h1 id="title">{{ title }}</h1>
            </div>
        </div>

        <div id="layout-subtitle">
            <h2 class="subtitle">{{ this.instruction() }}</h2>
        </div>
    </section>
</template>

<script>
    import { mapState } from "vuex"

    export default {
        name: "Title",
        props: {},
        computed: {
            ...mapState(["user", "currentSession", "isLoading"]),
            title() {
                return this.$route.meta.title
            },
            isAuth() {
                return this.$store.getters.isAuth
            }
        },
        methods: {
            instruction() {
                let title = this.$route.meta.instruction
                // Return default titles for all routes except Decision`s page
                if (this.$route.name != "Decision’s page") {
                    return title
                }

                // Custom route for Decision`s page
                if (!this.isLoading) {
                    title = `${this.currentSession["options"]["aliases"]["ticker"]} (timeframe: ${this.currentSession["options"]["aliases"]["timeframe"]})`
                }
                return title
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    .shift_header {
        margin: 55px auto 0px auto !important;
    }

    #title {
        margin-top: 92px;
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        z-index: 1;
        padding-top: 5px;
    }

    #title h1 {
        margin-top: 0px;
        margin-bottom: 0px;
        padding-top: 0px;
    }
    
    @media (max-width: 700px) {
        #title {
            font-size: 20px;
        }
    }

    #layout-title {
        height: 64px;
        margin: 15px 25px;
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

    #title-letter {
        font-size: 48px;
        font-weight: 900;
    }

    .subtitle {
        text-align: center;
        font-size: 14px;
        font-weight: 500;
    }

    @media (max-width: 380px) {
        .subtitle {
            font-size: 13px;
        }
    }

</style>
