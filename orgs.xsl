<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" 
	xmlns:commons="v3.commons.pure.atira.dk" 
	xmlns="v1.organisation-sync.pure.atira.dk"
	xmlns:python="python" exclude-result-prefixes="python">

<xsl:output method="xml" indent="yes" />


<!-- Passing this from Python -->
<xsl:param name="language"/>
<xsl:param name="country"/>

<!-- Locale - not we could grab this from Python, but this is to make it explicit
<xsl:variable name="language" select="'en'" />
<xsl:variable name="country" select="'US'" /> -->

<xsl:template match="root">
	<organisations>
		<xsl:comment>This data was auto-generated using a tool.</xsl:comment>
		
		<xsl:call-template name="organisation" />

		<xsl:apply-templates select="children/item" />

	</organisations>
</xsl:template>

<!-- The organisation -->
<xsl:template name="organisation">
	
	<organisation>
		<organisationId><xsl:value-of select="id" /></organisationId>
	        <type><xsl:value-of select="type"/></type>
	        <name>
	             <xsl:call-template name="text">
						<xsl:with-param name="val" select="name" />
				</xsl:call-template>
	       </name>
	        <startDate><xsl:value-of select="start_date" /></startDate>
	       <visibility>Public</visibility>

	       <xsl:call-template name="parent" />
	
	</organisation>

</xsl:template>

<!-- Set the org parent ID -->
<!-- Note: we have to go through the children to get the parent org. -->
<xsl:template name="parent">
	<xsl:if test="count(parent::children/parent::item/id | parent::children/parent::root/id)>0">
	<parentOrganisationId><xsl:value-of select="parent::children/parent::item/id | parent::children/parent::root/id" /></parentOrganisationId>
	</xsl:if>
</xsl:template>

<!-- Output each org recursively, while flattening -->
<xsl:template match="item">

	<xsl:call-template name="organisation" />
	<xsl:apply-templates select="children/item" />

</xsl:template>

<!-- Creates a localized string based on the language and country -->
<xsl:template name="text" >
	<xsl:param name="val" />
	<xsl:param name="escape" select="'no'" />

	<commons:text lang="{$language}" country="{$country}">
		<xsl:choose>
			<xsl:when test="$escape != ''">
				<xsl:value-of disable-output-escaping="yes" select="$val" />
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$val" />
			</xsl:otherwise>
		</xsl:choose>		
	</commons:text>
</xsl:template>

</xsl:transform>