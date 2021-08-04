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
        props: {
            page: {
                type: String,
                required: true,
                default: ''
            }
        },
        computed: {
            title() {
                switch(this.page) {
                    case '/login':
                        return 'Login page'
                    case '/session':
                        return 'Training session parameters'
                    case '/decision':
                        return 'Make a decision'
                    case '/scoreboard':
                        return 'Scoreboard'
                    default:
                        return 'Flash decision'
                }
            },
            instruction() {
                switch(this.page) {
                    case '/login':
                        return 'Please login to start your training session'
                    case '/session':
                        return 'Set parameters of the session and press Start'
                    case '/decision':
                        return 'You have 60 seconds to make a decision'
                    case '/scoreboard':
                        return 'Analyze your progress'
                    default:
                        return 'Instruction'
                }
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
        line-height: 50px;
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
