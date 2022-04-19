<script>
    var LabelsData = [
    <!-- {{ for i, marker in enumerate(map[0].markers)
        {
            name: "<!-- {{ '{}'.format(marker.name) }} -->",
            position: [<!-- {{ '{}'.format(marker.coord) }} -->],
            zooms: [10, 20],
            opacity: 1,
            zIndex: 10,
            icon: {
                type: 'image',
                image: 'https://a.amap.com/jsapi_demos/static/images/poi-marker.png',
                clipOrigin: [719, 0],
                clipSize: [50, 68],
                size: [25, 34],
                anchor: 'bottom-center',
                angel: 0,
                retina: true
            },
            text: {
                content: "<!-- {{ '{}'.format(marker.name) }} -->",
                direction: 'left',
                offset: [0, -5],
                style: {
                    fontSize: 11,
                    fontWeight: 'normal',
                    fillColor: 'red',
                    strokeColor: '#fff',
                    strokeWidth: 2,
                }
            }
        },
    }} -->
    ]

    var marker, map = new AMap.Map('container', {
        resizeEnable: true,
        zoom:13,
        center: [<!-- {{ '{}'.format(map[0].center) }} -->]
    });

    var layer = new AMap.LabelsLayer({
        zooms: [3, 20],
        zIndex: 1000,
        // 开启标注避让，默认为开启，v1.4.15 新增属性
        collision: true,
        // 开启标注淡入动画，默认为开启，v1.4.15 新增属性
        animation: true,
    });

    map.add(layer);
    var markers = [];
    for (var i = 0; i < LabelsData.length; i++) {
        var curData = LabelsData[i];
        curData.extData = {
            index: i
        };
        var labelMarker = new AMap.LabelMarker(curData);
        labelMarker.on('mouseover', function(e){
            var position = e.data.data && e.data.data.position;
            if(position){
                normalMarker.setContent(
                    '<div class="marker-info">'
                        + '<!-- {{ '{}'.format(marker.info) }} -->' +
                        '<div class="amap-info-sharp"></div>' +
                    '</div>');
                normalMarker.setPosition(position);
                map.add(normalMarker);
            }
        });

        labelMarker.on('mouseout', function(){
            map.remove(normalMarker);
        });
        markers.push(labelMarker);
    }
    layer.add(markers);
    var normalMarker = new AMap.Marker({
        offset: new AMap.Pixel(5, -10),
    });
</script>