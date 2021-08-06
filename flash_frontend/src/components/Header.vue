<template>
    <div id='header_layout'>
        <div id='header_left'>
            <div v-if='isAuth == true' class='header_button'>
                <img class='icon_margin_right' src='../assets/icons/i_header_user.svg'/>
                <p>{{ username }}</p>
            </div>
        </div>
        <div v-if='isAuth == true' id='header_right'>
            <a class='header_button' href='#'>
                <img class='icon_margin_right' src='../assets/icons/i_header_logout.svg'/>
                <p>logout</p>
            </a>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Header',
    props: {
        username: {
            type: String,
            required: true,
            default: 'username'
        },
        isAuth: {
            type: Boolean,
            required: true,
            default: false
        }
    }
}
</script>

<style>
    #header_layout {
        display: flex;
        flex-direction: row;
        width: 100%;
        height: 17px;
    }

    #header_left {
        width: 50%;
        text-align: left;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
    }

    #header_right {
        width: 50%;
        text-align: right;
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
        align-items: center;
    }

    .header_button {
        display: flex;
        flex-direction: row;
        cursor: pointer;
    }

    .icon_margin_right {
        margin: 0px 5px 0px 0px;
    }

</style>