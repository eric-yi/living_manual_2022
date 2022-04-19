<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>

    <!--js {{xlsx.full.min}} -->
    <!--js {{FileSaver.min}} -->
    <!--js {{living_manual_header_script}} -->


    <!--css {{living_manual_style}} -->
    <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css"/>
    <style>
    html,
    body,
    #map,
    #container {
        width: 100%;
        height: 100%;
    }
    .info{
        width: 32rem;
        top: 5rem;
    }
    .marker-info{
        font-size: 9px;
        line-height: 1;
        font-weight: 300;
        color: #ff6600;
        outline-offset: 3px;
        box-sizing: border-box;
        padding: .75rem 1.25rem;
        margin-bottom: 1rem;
        border-radius: .25rem;
        position: fixed;
        background-color: white;
        min-width: 10rem;
        border-width: 0;
        box-shadow: 0 2px 6px 0 rgba(114, 124, 245, .5);
        top: 1rem;
    }

    </style>

    <title>上海2022生活手册</title>
</head>
<body>
<ul class="menu">
    <li>
        <button data-panel="map" class="navbutton">防疫地图</button>
    </li>
    <li>
        <button data-panel="summary" class="navbutton">防疫报告</button>
    </li>
    <li>
        <button data-panel="resident" class="navbutton">防疫居住地</button>
    </li>
    <li>
        <button data-panel="vendor" class="navbutton">购买渠道</button>
    </li>
</ul>

<!--tpl {{living_manual_map}} -->
<!--tpl {{living_manual_summary}} -->
<!--tpl {{living_manual_resident}} -->
<!--tpl {{living_manual_vendor}} -->

<!--js {{list.min}} -->
<!--js {{panelsnap}} -->
<script type="text/javascript"
        src="https://webapi.amap.com/maps?v=1.4.15&key=您申请的key值"></script>
<!--js {{living_manual_bottom_script}} -->
<!--tpl {{living_manual_map_script}} -->
</body>
</html>