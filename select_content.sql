SELECT	CT.[Path]
        ,CT.[Type]
		,cc.ContentType
        ,CONVERT(varbinary(max), cc.[Content]) AS BinaryContent
FROM dbo.[Catalog] AS CT
		LEFT OUTER JOIN dbo.CatalogItemExtendedContent cc
			ON ct.ItemID = cc.ItemId
WHERE CT.[Type] IN (13) -- this idicates a PBI report
	AND cc.ContentType = 'CatalogItem';