<template>
    <section class='menu'>
            <router-link to='/session' tag="div" class='menu_button'>
                <img v-if='page == "/session"' src='../assets/icons/i_menu_session_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_session_inactive.svg' alt='Icon'>
                <p class='menu_text'>Session</p>
            </router-link>
            <router-link to='/decision' tag="div" class='menu_button'>
                <img v-if='page == "/decision"' src='../assets/icons/i_menu_decision_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_decision_inactive.svg' alt='Icon'>
                <p class='menu_text' >Decision</p>
            </router-link>
            <router-link to='/scoreboard' tag="div" class='menu_button'>
                <img v-if='page == "/scoreboard"' src='../assets/icons/i_menu_scoreboard_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_scoreboard_inactive.svg' alt='Icon'>
                <p class='menu_text'>Scoreboard</p>
            </router-link>
    </section>
</template>

<script>

    export default {
        name: 'Menu',
        props: {
            page: {
                type: String,
                required: true,
                default: ''
            }
        }
    }

</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style scoped>

    .menu {
        background: #E5E5E5;
        width: 100%;
        text-align: center;
        display: flex;
        flex-direction: row;
        align-items: center;
        border-bottom: 0.5px solid #0B5A73;
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
    }

    .menu_text {
        margin-left: 5px;
        font-weight: bold;
    }

    .router-link-active {
        background-color: #0B5A73;
        color: #ffffff;
    }

</style>
