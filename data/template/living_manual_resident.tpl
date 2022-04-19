<section data-panel="resident">
    <div class="info">
        <!--html {{statement}} -->
    </div>
    <div id="resident">
        <input class="search" placeholder="Search"/>
        <button class="sort" data-sort="published_date">发布日期</button>
        <button class="sort" data-sort="district">区域</button>
        <button id="export" onclick="export_excel('residentlist', 'residents')">导出</button>

        <table id="residentlist" border="1" class="ExcelTable2007">
            <tr>
                <th></th>
                <th>发布日期</th>
                <th>区域</th>
                <th>地址</th>
            </tr>
            <tbody class="list">

            <!-- {{ for i, resident in enumerate(residents)
            <tr>
                <td align="left" valign="bottom" class="heading"><!-- {{ '{}'.format(i+1) }} --></td>
                <td align="right" valign="bottom" class="published_date"><!-- {{ '{}'.format(resident.published_date) }} --></td>
                <td align="right" valign="bottom" class="district"><!-- {{ '{}'.format(resident.district) }} --></td>
                <td align="right" valign="bottom" class="address"><!-- {{ '{}'.format(resident.address) }} --></td>
            </tr>
            }} -->
            </tbody>
        </table>
    </div>
</section>