SELECT CT.[path],
       CT.[type],
       cc.contenttype,
       CONVERT(VARBINARY(max), cc.[content]) AS BinaryContent
FROM   dbo.[catalog] AS CT
       LEFT OUTER JOIN dbo.catalogitemextendedcontent cc
                    ON ct.itemid = cc.itemid
WHERE  CT.[type] IN ( 13 ) -- this idicates a PBI report
       AND cc.contenttype = 'CatalogItem'
       AND CT.ItemId = ?;
