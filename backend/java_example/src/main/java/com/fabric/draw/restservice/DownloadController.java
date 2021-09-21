package com.fabric.draw.restservice;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.StringReader;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonObject;
import javax.json.JsonReader;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;


@CrossOrigin(origins = "http://localhost:8080")
@RestController
public class DownloadController {

	@PostMapping("/download")
	public ResponseEntity<byte[]> download(@RequestBody Map<String,Object> params) {
		JsonReader jsonReader = Json.createReader(new StringReader((String) params.get("jsonContent")));
		JsonObject orgJson = jsonReader.readObject();
		String base = DownloadController.class.getResource("/").getPath().replaceFirst("/", "").replaceAll("/WEB-INF/classes/", "");
		File[] srcfile = {new File(base + "/template/build_env.sh"), 
				new File(base + "/template/configtx.yaml"),
				new File(base + "/template/docker-compose-ca.yaml"),
				new File(base + "/template/docker-compose-cli.yaml"),
				new File(base + "/template/setup.sh")};
		ByteArrayOutputStream bos = new ByteArrayOutputStream();
		try {
		ZipOutputStream out = new ZipOutputStream(bos);
		String createCommand = "";
		for (int i = 0; i < srcfile.length; i++) {
			Long filelength = srcfile[i].length();  
	        byte[] fileContent = new byte[filelength.intValue()]; 
	        FileInputStream in = new FileInputStream(srcfile[i]);
			out.putNextEntry(new ZipEntry(srcfile[i].getName()));
			in.read(fileContent);
			String strContent = new String(fileContent, "utf-8");
			if (srcfile[i].getName().equals("docker-compose-ca.yaml")) {
				File caFile = new File(base + "/template/ca-template.yaml");
				filelength = caFile.length();
		        byte[] caContent = new byte[filelength.intValue()]; 
		        FileInputStream caIn = new FileInputStream(caFile);
		        caIn.read(caContent);
		        String caStrContent = new String(caContent, "utf-8");
		        strContent = strContent.replace("{{DOMAIN_NETWORK}}", "test");
		        int port = 7;
			    for (int index = 0; index < orgJson.size(); index++, port++) {
			    	JsonObject org = orgJson.getJsonObject(String.valueOf(index));
			    	String partStrContent = caStrContent.replace("{{DOMAIN_NAME}}", org.getString("domain"));
			    	partStrContent = partStrContent.replace("{{DOMAIN_NETWORK}}", "test");
			    	partStrContent = partStrContent.replace("{{ORG_NAME}}", org.getString("name"));
			    	partStrContent = partStrContent.replace("{{OUT_PORT}}", port + "054");
			    	strContent += partStrContent;
			    }
			    out.write(strContent.getBytes());
			    caIn.close();
			}
			else if (srcfile[i].getName().equals("docker-compose-cli.yaml")) {
				File ordererFile = new File(base + "/template/orderer-template.yaml");
				filelength = ordererFile.length();
		        byte[] ordererContent = new byte[filelength.intValue()]; 
		        FileInputStream ordererIn = new FileInputStream(ordererFile);
		        ordererIn.read(ordererContent);
		        String ordererStrContent = new String(ordererContent, "utf-8");
		        strContent = strContent.replace("{{DOMAIN_NETWORK}}", "test");
			    int index = 0;
		    	JsonObject org = orgJson.getJsonObject(String.valueOf(index));
		    	String partStrContent = "";
		    	int port = 7;
		    	createCommand += "create_orderer_org " + org.getString("name") + " " + org.getString("domain") + " 7054\r\n";
		    	for (String key : org.getJsonObject("peerName").keySet()) {
			    	partStrContent = ordererStrContent.replace("{{DOMAIN_NAME}}", org.getString("domain"));
			    	partStrContent = partStrContent.replace("{{DOMAIN_NETWORK}}", "test");
			    	partStrContent = partStrContent.replace("{{ORG_MSP}}", toUpperCaseFirstOne(org.getString("name")) + "MSP");
			    	partStrContent = partStrContent.replace("{{PEER_NAME}}", org.getJsonObject("peerName").getString(key));
			    	partStrContent = partStrContent.replace("{{OUT_PORT}}", port + "050");
			    	port++;
			    	strContent += partStrContent;
			    	createCommand += "create_orderer " + org.getJsonObject("peerName").getString(key) + " " + org.getString("domain") + " 7054\r\n";
		    	}
		    	File peerFile = new File(base + "/template/peer-template.yaml");
				filelength = peerFile.length();
		        byte[] peerContent = new byte[filelength.intValue()]; 
		        FileInputStream peerIn = new FileInputStream(peerFile);
		        peerIn.read(peerContent);
		        String peerStrContent = new String(peerContent, "utf-8");
		    	port = 7;
			    for (index = 1; index < orgJson.size(); index++) {	
			    	createCommand += "create_org " + org.getString("name") + " " + org.getString("domain") + " " + (7 + index) + "054\r\n";
			    	org = orgJson.getJsonObject(String.valueOf(index));
			    	for (String key : org.getJsonObject("peerName").keySet()) {
				    	partStrContent = peerStrContent.replace("{{DOMAIN_NAME}}", org.getString("domain"));
				    	partStrContent = partStrContent.replace("{{DOMAIN_NETWORK}}", "test");
				    	partStrContent = partStrContent.replace("{{ORG_MSP}}", toUpperCaseFirstOne(org.getString("name")) + "MSP");
				    	partStrContent = partStrContent.replace("{{ORG_NAME}}", org.getString("name"));
				    	partStrContent = partStrContent.replace("{{PEER_NAME}}", org.getJsonObject("peerName").getString(key));
				    	partStrContent = partStrContent.replace("{{OUT_PORT}}", port + "051");
				    	port++;
				    	strContent += partStrContent;
				    	createCommand += "create_peer " + org.getString("name") + " " + org.getJsonObject("peerName").getString(key) + " " + org.getString("domain") + " " + (7 + index) + "054\r\n";
			    	}
			    }
			    File cliFile = new File(base + "/template/cli-template.yaml");
				filelength = cliFile.length();
		        byte[] cliContent = new byte[filelength.intValue()]; 
		        FileInputStream cliIn = new FileInputStream(cliFile);
		        cliIn.read(cliContent);
		        String cliStrContent = new String(cliContent, "utf-8");
		        strContent += cliStrContent.replace("{{DOMAIN_NETWORK}}", "test");
			    out.write(strContent.getBytes());
			    ordererIn.close();
			    peerIn.close();
			    cliIn.close();
			}
			else if (srcfile[i].getName().equals("setup.sh")) {
				createCommand += "\r\n" + "docker-compose -f docker-compose-cli.yaml up -d\r\n";
			    strContent += createCommand;
				out.write(strContent.getBytes());
			}
			else {
			    out.write(strContent.getBytes());
			}
            out.closeEntry();
            in.close();
		}
		out.close();
        bos.close();
		} catch (Exception e) {
	        e.printStackTrace();
	    }
		HttpHeaders header = new HttpHeaders();
	    header.add("Content-Disposition", "attachment;filename=fabbric.zip");
	    return new ResponseEntity<byte[]>(bos.toByteArray(), header, HttpStatus.CREATED);
	}
	
	public static String toUpperCaseFirstOne(String s){
			if(Character.isUpperCase(s.charAt(0)))
				return s;
			else
				return (new StringBuilder()).append(Character.toUpperCase(s.charAt(0))).append(s.substring(1)).toString();
	}
}
