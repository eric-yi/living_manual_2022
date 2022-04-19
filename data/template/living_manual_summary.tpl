<section data-panel="summary">
    <div class="info">
       <!--html {{statement}} -->
    </div>
    <div id="summary">
        <input class="search" placeholder="Search"/>
        <button class="sort" data-sort="published_date">发布日期</button>
        <button class="sort" data-sort="district">区域</button>
        <button id="export" onclick="export_excel('summarylist', 'summaries')">导出</button>

        <table id="summarylist" border="1" class="ExcelTable2007">
            <tr>
                <th></th>
                <th>发布日期</th>
                <th>区域</th>
                <th>本土确诊病例</th>
                <th>本土无症状感染者</th>
            </tr>
            <tbody class="list">

            <!-- {{ for i, summary in enumerate(summaries)
            <tr>
                <td align="left" valign="bottom" class="heading"><!-- {{ '{}'.format(i+1) }} --></td>
                <td align="right" valign="bottom" class="published_date"><!-- {{ '{}'.format(summary.published_date) }} --></td>
                <td align="right" valign="bottom" class="district"><!-- {{ '{}'.format(summary.district) }} --></td>
                <td align="right" valign="bottom" class="diagnosed"><!-- {{ '{}'.format(summary.diagnosed) }} --></td>
                <td align="right" valign="bottom" class="asymptomatic"><!-- {{ '{}'.format(summary.asymptomatic) }} --></td>
            </tr>
            }} -->
            </tbody>
        </table>
    </div>
</section>