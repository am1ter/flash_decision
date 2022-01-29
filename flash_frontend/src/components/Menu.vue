<template>
    <section id='menu' :class='{ disabled: !isAuth }'>
            <router-link to='/session' tag="div" class='menu_button' :class='{ "menu-active": check_is_page_active("session") }'>
                <img v-if='check_is_page_active("session")' src='../assets/icons/i_menu_session_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_session_inactive.svg' alt='Icon'>
                <p class='menu_text'>Session</p>
            </router-link>
            <router-link to='/decision' tag="div" class='menu_button' :class='{ "menu-active": check_is_page_active("decision") }'>
                <img v-if='check_is_page_active("decision")' src='../assets/icons/i_menu_decision_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_decision_inactive.svg' alt='Icon'>
                <p class='menu_text' >Decision</p>
            </router-link>
            <router-link to='/scoreboard' tag="div" class='menu_button' :class='{ "menu-active": check_is_page_active("scoreboard") }'>
                <img v-if='check_is_page_active("scoreboard")' src='../assets/icons/i_menu_scoreboard_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_scoreboard_inactive.svg' alt='Icon'>
                <p class='menu_text'>Scoreboard</p>
            </router-link>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    export default {
        name: 'Menu',
        props: {},
        computed: {
            ...mapState(['isAuth'])
        },
        methods: {
            check_is_page_active(menu_element) {
                let menu_paths = {
                    'session': ['session'],
                    'decision': ['decision', 'sessions-results'],
                    'scoreboard': ['scoreboard']
                }
                let current_page = this.$route.path.split('/')[1]
                return menu_paths[menu_element].indexOf(current_page) >= 0
            }
        }
    }
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style scoped>

    #menu {
        background: #E5E5E5;
        width: 100%;
        text-align: center;
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .menu_button {
        flex: 1;
        width: 100%;
        height: 100%;
        font-family: Roboto;
        color: #333333;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        border-bottom: 1px solid #0B5A73;
    }

    .menu_button:hover {
        box-shadow: 0px -1px 0px #271238 inset;
    }

    .menu_button.router-link-active:hover {
        background-color: #0c4e63;
    }

    .menu_button:hover:not(.router-link-active) {
        background-color: #ffffff;
    }


    .menu_text {
        margin: 15px 5px;
        font-weight: 500;
    }

    .router-link-active {
        background-color: #0B5A73;
        color: #ffffff;
        box-shadow: 0px -1px 0px #333333 inset;
    }
    
    .menu-active {
        background-color: #0B5A73;
        color: #ffffff;
        box-shadow: 0px -1px 0px #333333 inset;
    }   

    .menu-active:hover {
        background-color: #0c4e63 !important;
    }

</style>
