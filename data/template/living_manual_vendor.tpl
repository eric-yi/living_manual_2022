 <section data-panel="vendor">
    <div class="info">
        <!--html {{statement}} -->
    </div>
    <div id="vendor">
        <input class="search" placeholder="Search"/>
        <button class="sort" data-sort="district">区域</button>
        <button class="sort" data-sort="category">分类</button>
        <button class="sort" data-sort="available_date">有效时间</button>
        <button class="sort" data-sort="record_date">录入时间</button>
        <button id="export" onclick="export_excel('vendorlist', 'vendor')">导出</button>
    
        <table id="vendorlist" border="1" class="ExcelTable2007">
            <tr>
                <th></th>
                <th>区域</th>
                <th>供应商</th>
                <th>联系人</th>
                <th>地址</th>
                <th>电话</th>
                <th>分类</th>
                <th>描述</th>
                <th>来源</th>
                <th>订购方式</th>
                <th>订购条件</th>
                <th>链接</th>
                <th>有效时间</th>
                <th>录入时间</th>
                <th>标签</th>
            </tr>

            <tbody class="list">

            <!-- {{ for i, vendor in enumerate(vendors)
            <tr>
                <td align="left" valign="bottom" class="heading"><!-- {{ "{}".format(i+1) }} --></td>
                <td align="right" valign="bottom" class="district"><!-- {{ "{}".format(vendor.district) }} --></td>
                <td align="right" valign="bottom" class="vendor"><!-- {{ "{}".format(vendor.name) }} --></td>
                <td align="right" valign="bottom" class="contact"><!-- {{ "{}".format(vendor.contact) }} --></td>
                <td align="right" valign="bottom" class="address"><!-- {{ "{}".format(vendor.address) }} --></td>
                <td align="right" valign="bottom" class="mobile"><!-- {{ "{}".format(vendor.mobile) }} --></td>
                <td align="right" valign="bottom" class="category"><!-- {{ "{}".format(vendor.category) }} --></td>
                <td align="right" valign="bottom" class="desc"><!-- {{ "{}".format(vendor.desc) }} --></td>
                <td align="right" valign="bottom" class="origin"><!-- {{ "{}".format(vendor.origin) }} --></td>
                <td align="right" valign="bottom" class="order_type"><!-- {{ "{}".format(vendor.order_type) }} --></td>
                <td align="right" valign="bottom" class="available_desc"><!-- {{ "{}".format(vendor.available_desc) }} --></td>
                <td align="right" valign="bottom" class="order_type"><!-- {{ "{}".format(vendor.link) }} --></td>
                <td align="right" valign="bottom" class="available_date"><!-- {{ "{}".format(vendor.available_date) }} --></td>
                <td align="right" valign="bottom" class="record_date"><!-- {{ "{}".format(vendor.record_date) }} --></td>
                <td align="right" valign="bottom" class="tag"><!-- {{ "{}".format(vendor.tag) }} --></td>
            </tr>
            }} -->
            </tbody>
        </table>
    </div>
</section>
