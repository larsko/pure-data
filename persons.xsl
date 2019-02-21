<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" 
	xmlns:commons="v3.commons.pure.atira.dk" 
	xmlns="v1.unified-person-sync.pure.atira.dk"
	xmlns:python="python" exclude-result-prefixes="python">

<xsl:output method="xml" indent="yes" />

<!-- Passing this from Python -->
<xsl:param name="language"/>
<xsl:param name="country"/>

<!-- Locale - not we could grab this from Python, but this is to make it explicit 
<xsl:variable name="language" select="'en'" />
<xsl:variable name="country" select="'US'" />-->

<xsl:template match="root">
	<persons>
		<xsl:comment>This data was auto-generated using a tool.</xsl:comment>
		<xsl:apply-templates select="item" />

	</persons>
</xsl:template>

<xsl:template match="item">
	
	<person id="{id}" managedInPure="false">

		<name>
			<commons:firstname><xsl:value-of select="firstname" /></commons:firstname>
			<commons:lastname><xsl:value-of select="lastname" /></commons:lastname>
		</name>

		<xsl:apply-templates select="names" />

		<xsl:apply-templates select="titles" />

		<gender><xsl:value-of select="gender" /></gender>
		
		<xsl:apply-templates select="dob" />
		
		<xsl:apply-templates select="nationality" />
		
		<xsl:apply-templates select="employeeStartDate" />
		
		<!--<systemLeavingDate></systemLeavingDate>
		
		<academicProfessionEntry></academicProfessionEntry>
		
		<retiralDate></retiralDate>-->
		
		<xsl:apply-templates select="privateAddress" />
		
		<expert>true</expert>
		
		<!--<leavesOfAbsence></leavesOfAbsence>-->
		
		<xsl:apply-templates select="willingness_to_phd" />
		
		<xsl:apply-templates select="photos" />
		
		<xsl:apply-templates select="phd_research_projects"/>
		
		<xsl:apply-templates select="organisationAssociations" />
		
		<!-- <affiliationNote></affiliationNote> -->
		
		<xsl:apply-templates select="education" />
		
		<xsl:apply-templates select="external_positions" />
		 
		<xsl:apply-templates select="profile_information" />
<!--
		<professionalQualifications></professionalQualifications>

		<keywords></keywords> -->

		<xsl:apply-templates select="links" />

		<xsl:apply-templates select="user" />

		<xsl:apply-templates select="ids" />

		<xsl:apply-templates select="orcid"/>

		<visibility><xsl:value-of select="visibility" /></visibility>

		<xsl:apply-templates select="profiled" />
	</person>

</xsl:template>

<xsl:template match="profile_information">
        <profileInformation>
        <personCustomField id="{id}">
            <typeClassification>researchinterests</typeClassification>
            <value>
                <xsl:call-template name="text">
					<xsl:with-param name="val" select="text" />
				</xsl:call-template>
            </value>
        </personCustomField>
    </profileInformation>
</xsl:template>

<xsl:template match="external_positions">
	<externalPositions>

	<xsl:for-each select="*">
	
		<externalPosition id="{id}">
                <startDate>
                    <commons:year><xsl:value-of select="start_date/y" /></commons:year>
                    <commons:month><xsl:value-of select="start_date/m" /></commons:month>
                    <commons:day><xsl:value-of select="start_date/d" /></commons:day>
                </startDate>
                <endDate>
                    <commons:year><xsl:value-of select="end_date/y" /></commons:year>
                    <commons:month><xsl:value-of select="end_date/m" /></commons:month>
                    <commons:day><xsl:value-of select="end_date/d" /></commons:day>
                </endDate>
                <!--<appointment><xsl:value-of select="appointment" /></appointment>-->
                <appointmentString><xsl:value-of select="appointment" /></appointmentString>
                <externalOrganisationAssociation>
                    <externalOrganisation>
                    	<name><xsl:value-of select="organisation" /></name>
                    </externalOrganisation>
                </externalOrganisationAssociation>
            </externalPosition>

	</xsl:for-each>

	</externalPositions>
</xsl:template>

<xsl:template match="employeeStartDate">
	<employeeStartDate><xsl:value-of select="." /></employeeStartDate>
</xsl:template>

<xsl:template match="nationality">
	<nationality><xsl:value-of select="." /></nationality>
</xsl:template>

<xsl:template match="dob">
	<dateOfBirth><xsl:value-of select="." /></dateOfBirth>
</xsl:template>

<xsl:template match="orcid">
	<orcId><xsl:value-of select="." /></orcId>
</xsl:template>

<xsl:template match="profiled">
	<profiled><xsl:value-of select="." /></profiled>
</xsl:template>

<!-- the person org associations -->
<!-- TODO: can expand on the different additional content here... -->
<xsl:template match="organisationAssociations">
	<organisationAssociations>
		<xsl:for-each select="*">
			<xsl:element name="{association}">
				<xsl:attribute name="id"><xsl:value-of select="id" /></xsl:attribute>

				<xsl:apply-templates select="phone_numbers"/>
				<xsl:apply-templates select="emails"/>
				<xsl:apply-templates select="websites"/>
				<!--<employmentType><xsl:value-of select="employment" /></employmentType>-->
				<xsl:if test="primary='true'">
					<primaryAssociation><xsl:value-of select="primary" /></primaryAssociation>
				</xsl:if>
                <organisation>
                    <commons:non_explicit_id><xsl:value-of select="organisation_id"/></commons:non_explicit_id>
                </organisation>
                <period>
                    <commons:startDate><xsl:value-of select="start" /></commons:startDate>
                    <xsl:if test="end != ''">
                    	<commons:endDate>
                    		<xsl:value-of select="end" />
                    	</commons:endDate>
                    </xsl:if>
                </period>

                <xsl:choose>
                	<xsl:when test="association = 'staffOrganisationAssociation'">
                		<staffType><xsl:value-of select="type" /></staffType>
		                <!--<contractType>fixedterm</contractType>-->
		                <!--<jobTitle>juniorprofessor</jobTitle>-->
		                <jobDescription>
		                    <xsl:call-template name="text">
								<xsl:with-param name="val" select="job_description" />
							</xsl:call-template>
		                </jobDescription>
                	</xsl:when>
                	<xsl:otherwise></xsl:otherwise>
                </xsl:choose>

               </xsl:element>
		</xsl:for-each>
	</organisationAssociations>
</xsl:template>

<!-- note: only supports 1 phone number currently -->
<xsl:template match="phone_numbers">

    <phoneNumbers>
        <commons:classifiedPhoneNumber id="{id}">
            <commons:classification>phone</commons:classification>
            <commons:value><xsl:value-of select="value" /></commons:value>
        </commons:classifiedPhoneNumber>
    </phoneNumbers>	

</xsl:template>

<!-- note: only supports 1 email currently -->
<xsl:template match="emails">

    <emails>
        <commons:classifiedEmail id="{id}">
            <commons:classification>email</commons:classification>
            <commons:value><xsl:value-of select="value" /></commons:value>
        </commons:classifiedEmail>
    </emails>	

</xsl:template>

<!-- note: only supports 1 website currently -->
<xsl:template match="websites">

    <webAddresses>
        <commons:classifiedWebAddress id="{id}">
            <commons:classification>web</commons:classification>
            <commons:value>
                 <xsl:call-template name="text">
						<xsl:with-param name="val" select="value" />
					</xsl:call-template>
            </commons:value>
        </commons:classifiedWebAddress>
    </webAddresses>

</xsl:template>

<!-- person name variants -->
<xsl:template match="names">
	
	<names>
		<xsl:for-each select="*">
			<classifiedName id="{name()}">
				<name>
					<commons:firstname><xsl:value-of select="firstname" /></commons:firstname>
	                <commons:lastname><xsl:value-of select="lastname" /></commons:lastname>
				</name>
				<typeClassification><xsl:value-of select="name()" /></typeClassification>
			</classifiedName>
		</xsl:for-each>
	</names>

</xsl:template>

<!-- person private address info -->
<xsl:template match="privateAddress">
	
    <privateAddress>
        <commons:country><xsl:value-of select="country" /></commons:country>
        <commons:road><xsl:value-of select="address" /></commons:road>
        <commons:room><xsl:value-of select="room" /></commons:room>
        <commons:city><xsl:value-of select="city" /></commons:city>
        <commons:building><xsl:value-of select="building" /></commons:building>
        <commons:postalCode><xsl:value-of select="zip" /></commons:postalCode>
    </privateAddress>

</xsl:template>

<!-- person willing to take phd students -->
<xsl:template match="willingness_to_phd">
	<willingnessToPhd><xsl:value-of select="." /></willingnessToPhd>
</xsl:template>

<!-- person phd projects - think this is legacy -->
<xsl:template match="phd_research_projects">
	<phdResearchProjects><xsl:value-of select="phdResearchProjects" /></phdResearchProjects>
</xsl:template>

<!-- person titles - ensure that typeClassification exists in Pure -->
<xsl:template match="titles">
	<titles>
		<xsl:for-each select="*">
			<title id="{name()}">
				<typeClassification><xsl:value-of select="name()" /></typeClassification>
				<value>
					<xsl:call-template name="text">
						<xsl:with-param name="val" select="text()" />
					</xsl:call-template>
				</value>
			</title>	
		</xsl:for-each>
	</titles>
</xsl:template>

<!-- person links -->
<xsl:template match="links">
	<links>
		<xsl:for-each select="*">
			<commons:link id="{name()}">
				<commons:url><xsl:value-of select="url" /></commons:url>
				<commons:type><xsl:value-of select="name()" /></commons:type>
				<commons:description>
					<xsl:call-template name="text">
						<xsl:with-param name="val" select="description" />
					</xsl:call-template>
				</commons:description>
			</commons:link>
		</xsl:for-each>
	</links>
</xsl:template>

<xsl:template match="ids">
	
	<personIds>
		<xsl:for-each select="item">
			<commons:id type="{type}" id="{id}"><xsl:value-of select="id" /></commons:id>
		</xsl:for-each>
	</personIds>

</xsl:template>

<xsl:template match="education">

	<personEducations>
		<personEducation id="{id}">
			<startDate>
				<commons:year><xsl:value-of select="start_date/y" /></commons:year>
                <commons:month><xsl:value-of select="start_date/m" /></commons:month>
                <commons:day><xsl:value-of select="start_date/d" /></commons:day>
			</startDate>
			<endDate>
				<commons:year><xsl:value-of select="end_date/y" /></commons:year>
                <commons:month><xsl:value-of select="end_date/m" /></commons:month>
                <commons:day><xsl:value-of select="end_date/d" /></commons:day>
			</endDate>
			<fieldOfStudy>unknown</fieldOfStudy>
			<qualificationString>
				<xsl:call-template name="text">
					<xsl:with-param name="val" select="academic_degree" />
				</xsl:call-template>
			</qualificationString>
			<!-- dont rely on classifications <qualification><xsl:value-of select="academic_degree" /></qualification>-->
			<!-- right now we only support external orgs... -->
			<organisations>
				<externalOrganisationAssociation>
					<externalOrganisation>
						<name><xsl:value-of select="organisation" /></name>
					</externalOrganisation>
				</externalOrganisationAssociation>
			</organisations>
			<projectTitle>
				<xsl:call-template name="text">
					<xsl:with-param name="val" select="project" />
				</xsl:call-template>
			</projectTitle>
			<awardDate><xsl:value-of select="award_date" /></awardDate>
		</personEducation>
	</personEducations>

</xsl:template>

<xsl:template match="user">
	<user id="{userName}">
		<userName><xsl:value-of select="userName" /></userName>
		<email><xsl:value-of select="email" /></email>
	</user>
</xsl:template>

<xsl:template match="photos">
	<photos>
		<xsl:for-each select="*">
			<personPhoto id="{id}">
				<classification><xsl:value-of select="name()" /></classification>
				<data>
					<http>
						<url><xsl:value-of select="url" /></url>
						<fileName><xsl:value-of select="filename" />.jpg</fileName>
					</http>
				</data>
			</personPhoto>
		</xsl:for-each>
	</photos>
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