from lxml import etree

def imdb_person_transform(person_role='cast'):
    """
    Create an XSLT transformation to extract person data for a specific role from an IMDb movie XML.

    Parameters
    ----------
    person_role : str, optional
        The role of the person in the movie, e.g., 'cast', 'director', etc. (default is 'cast')

    Returns
    -------
    lxml.etree.XSLT
        The XSLT transformation for extracting person data of the specified role.
    """
    xsl_root = etree.XML('''\
    <xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Name</th>
            </tr>
            <xsl:apply-templates /> 
        </table>
    </xsl:template>
    <xsl:template match="movie/{role1}">
    <xsl:for-each select="person">
        <tr>
            <td><xsl:value-of select="@id"/></td>
            <td><xsl:value-of select="name"/></td>
        </tr>
    </xsl:for-each>
    </xsl:template>
    </xsl:stylesheet>
    '''.format(role1=person_role))
    return etree.XSLT(xsl_root)


def imdb_company_transform(company_role='production-companies'):
    """
    Create an XSLT transformation to extract company data for a specific role from an IMDb movie XML.

    Parameters
    ----------
    company_role : str, optional
        The role of the company in the movie, e.g., 'production-companies' (default is 'production-companies')

    Returns
    -------
    lxml.etree.XSLT
        The XSLT transformation for extracting company data of the specified role.
    """
    xsl_root = etree.XML('''\
    <xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Name</th>
            </tr>
            <xsl:apply-templates /> 
        </table>
    </xsl:template>
    <xsl:template match="movie/{role1}">
    <xsl:for-each select="company">
        <tr>
            <td><xsl:value-of select="@id"/></td>
            <td><xsl:value-of select="name"/></td>
        </tr>
    </xsl:for-each>
    </xsl:template>
    </xsl:stylesheet>
    '''.format(role1=company_role))
    return etree.XSLT(xsl_root) 


def imdb_movie_transform():
    """
    Create an XSLT transformation to extract movie data from an IMDb movie XML.

    Returns
    -------
    lxml.etree.XSLT
        The XSLT transformation for extracting movie data.
    """
    xsl_root = etree.XML('''\
    <xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Runtime</th>
                <th>Budget</th>
                <th>Opening Weekend</th>
                <th>Worldwide Gross</th>
                <th>Rating</th>
                <th>Votes</th>
                <th>Cover URL</th>
                <th>Cover URL full</th>
                <th>Plot Outline</th>
                <th>Year</th>
                <th>Plot</th>
                <th>Synopsis</th>
                <th>Locations</th>
                <th>Genres</th>
            </tr>
            <xsl:apply-templates /> 
        </table>
    </xsl:template>
    <xsl:template match="movie">
        <tr>
            <td><xsl:value-of select="@id"/></td>
            <td><xsl:value-of select="localized-title"/></td>
            <td><xsl:value-of select="runtimes/item" /></td>
            <td><xsl:value-of select="box-office/budget" /></td>
            <td><xsl:value-of select="box-office/opening-weekend-united-states" /></td>
            <td><xsl:value-of select="box-office/cumulative-worldwide-gross" /></td>
            <td><xsl:value-of select="rating" /></td>
            <td><xsl:value-of select="votes" /></td>
            <td><xsl:value-of select="cover-url" /></td>
            <td><xsl:value-of select="full-size-cover-url" /> </td>
            <td><xsl:value-of select="plot-outline" /></td>
            <td><xsl:value-of select="year" /></td>
            <td><xsl:value-of select="plot"/></td>
            <td><xsl:value-of select="synopsis"/></td>
            <td><xsl:value-of select="locations"/></td>
            <td>
                <xsl:for-each select="genres/item">
                    <xsl:value-of select="."/>;
                </xsl:for-each>
            </td>
            
        </tr>
  
    </xsl:template>
    </xsl:stylesheet>
    ''')
    return etree.XSLT(xsl_root)